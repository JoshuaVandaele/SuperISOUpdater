import asyncio
import contextlib
import re
import shutil
from pathlib import Path
from typing import Callable

from torrentp import TorrentDownloader

from modules.Checksum import Checksum, SHA1Sum, SHA256Sum
from modules.exceptions import IntegrityCheckError
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp


# TODO: Create a GenericTorrentMirror then have KaliLinux extend that instead of GenericHTTPMirror.
# Because this is currently the only mirror that uses torrents, I'm not sure of all the requirements yet, but some stoppers are:
# - What do we do if torrents contain multiple files? (e.g. multiple ISOs, or an ISO and a checksum file) Can we select which file(s) to download?
# - How do we create a "self.speed" value for a torrent mirror that is fair to both torrent and non-torrent mirrors?
# - In general, how do we make this as generic as possible to fit other torrent-based mirrors
# Some notes:
# - GenericTorrentMirror must be able to verify either one, or both the torrent file and the downloaded file, depending on what checksums and signatures are available for each. Those may be in separate files in separate locations, or in the same file.
# - We want to support mirrors that use magnet links instead of torrent files
# - We currently rely on torrentp to do the actual torrent downloading, but we may want to implement our own torrent downloading in the future if we need more control over the process (e.g. selecting which files to download from a torrent, or integrating with our existing download manager for speed testing and such), which would mean using libtorrent (which is a wrapper for libtorrent-rasterbar and not libtorrent-rtorrent)
class KaliLinuxTorrent(GenericHTTPMirror):
    def __init__(self, arch: str, edition: str) -> None:
        self.torrent_checksums: list[Checksum] = []
        self.iso_checksums: list[Checksum] = []
        super().__init__(
            uri="https://cdimage.kali.org/current/",
            download_regex=rf"kali-linux-([\d\.]+)-{edition}-{arch}\.iso\.torrent",
            version_regex=rf"kali-linux-([\d\.]+)-{edition}-{arch}\.iso",
            signed_file=download_file_to_tmp(
                "https://cdimage.kali.org/current/SHA256SUMS"
            ),
        )
        self.checksums: None
        self._version_regex: re.Pattern

    def _init_checksums(self) -> None:
        self._determine_sums()

    def _determine_sums(self):
        self.torrent_checksums = self._determine_torrent_sums()
        self.iso_checksums = self._determine_iso_sums()

    def __extract_sums(
        self, sumfile_content: str, condition: Callable[[str], bool | None]
    ) -> str | None:
        return next(
            (
                line.split()[0]
                for line in sumfile_content.splitlines()
                if condition(line)
            ),
            None,
        )

    def _determine_torrent_sums(self) -> list[Checksum]:
        sums: list[Checksum] = []
        r1 = self.session.get(f"{self.uri}/SHA1SUMS")
        r1.raise_for_status()
        sha1_sum = self.__extract_sums(
            r1.text,
            lambda line: re.search(self._download_regex, line) and "torrent" in line,
        )
        if not sha1_sum:
            raise ValueError("No torrent checksum found in SHA1SUMS file")
        sums.append(SHA1Sum(sha1_sum))

        r256 = self.session.get(f"{self.uri}/SHA256SUMS")
        r256.raise_for_status()
        sha256_sum = self.__extract_sums(
            r256.text,
            lambda line: re.search(self._download_regex, line) and "torrent" in line,
        )
        if not sha256_sum:
            raise ValueError("No torrent checksum found in SHA256SUMS file")
        sums.append(SHA256Sum(sha256_sum))
        return sums

    def _determine_iso_sums(self) -> list[Checksum]:
        sums: list[Checksum] = []
        r1 = self.session.get(f"{self.uri}/SHA1SUMS")
        r1.raise_for_status()
        sha1_sum = self.__extract_sums(
            r1.text,
            lambda line: re.search(self._version_regex, line) and "torrent" not in line,
        )
        if not sha1_sum:
            raise ValueError("No ISO checksum found in SHA1SUMS file")
        sums.append(SHA1Sum(sha1_sum))

        r256 = self.session.get(f"{self.uri}/SHA256SUMS")
        r256.raise_for_status()
        sha256_sum = self.__extract_sums(
            r256.text,
            lambda line: re.search(self._version_regex, line) and "torrent" not in line,
        )
        if not sha256_sum:
            raise ValueError("No ISO checksum found in SHA256SUMS file")
        sums.append(SHA256Sum(sha256_sum))
        return sums

    def download_and_verify(self, file) -> None:
        with contextlib.ExitStack() as stack:
            torrent_file = Path(f"{file}.torrent")
            stack.callback(torrent_file.unlink, missing_ok=True)

            self._download_file(torrent_file)

            if not self.checksum_file(torrent_file, self.torrent_checksums):
                raise IntegrityCheckError(
                    "Integrity check failed for torrent file! (Checksum)"
                )

            torrent_folder = Path(f"{torrent_file}.d")
            stack.callback(shutil.rmtree, torrent_folder, ignore_errors=True)

            try:
                tdl = TorrentDownloader(str(torrent_file), str(torrent_folder))
                asyncio.run(tdl.start_download())
            except Exception as e:
                raise IntegrityCheckError(f"Failed to download {file}") from e

            downloaded_iso = next(torrent_folder.glob("*.iso"), None)
            if not downloaded_iso:
                raise IntegrityCheckError(
                    "Downloaded torrent did not contain an ISO file"
                )

            self.signature_check(downloaded_iso)

            if not self.checksum_file(downloaded_iso, self.iso_checksums):
                raise IntegrityCheckError(
                    "Integrity check failed for ISO file! (Checksum)"
                )
            downloaded_iso.rename(file)

    def _determine_signature(self) -> bytes:
        r = self.session.get(f"{self.uri}/SHA256SUMS.gpg")
        r.raise_for_status()
        return r.content

    def _determine_public_key(self) -> bytes | None:
        # https://www.kali.org/docs/introduction/download-official-kali-linux-images/#verifying-your-downloaded-kali-image
        r = self.session.get("https://archive.kali.org/archive-key.asc")
        r.raise_for_status()
        return r.content
