from functools import cache
from urllib.parse import urljoin

from modules.Checksum import Checksum, SHA256Sum
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp, parse_hash


class OVH(GenericHTTPMirror):
    def __init__(self, arch: str, edition: str) -> None:
        def signed_file(self):
            return download_file_to_tmp(f"{self.download_link}/../CHECKSUM")

        super().__init__(
            uri="https://rockylinux.mirrors.ovh.net/",
            # For some reason, sometimes there is a "1" after the edition e.g. dvd1
            file_regex=rf"Rocky-([\d.]+)-{arch}-{edition}.\.iso",
            version_regex=rf"Rocky-([\d.]+)-{arch}-{edition}.\.iso",
            signed_file=signed_file,
        )
        r = self.session.get(urljoin(self.uri, "fullfilelist"))
        r.raise_for_status()
        self.full_file_list: list[str] = r.text.splitlines()

    @cache
    def _urls(self) -> list[str]:
        return [urljoin(self.uri, path) for path in self.full_file_list]

    def _determine_sums(self) -> list[Checksum]:
        r = self.session.get(f"{self.download_link}/../CHECKSUM")
        r.raise_for_status()
        lines = "\n".join([line for line in r.text.splitlines() if "=" in line])
        return [SHA256Sum(parse_hash(lines, self._file_regex, -1))]

    def _determine_public_key(self) -> bytes:
        # https://rockylinux.org/resources/gpg-key-info
        r = self.session.get(
            f"https://dl.rockylinux.org/pub/rocky/RPM-GPG-KEY-Rocky-{self.version.components[0]}"
        )
        r.raise_for_status()
        return r.content

    def _determine_signature(self) -> bytes:
        r = self.session.get(f"{self.download_link}/../CHECKSUM.asc")
        r.raise_for_status()
        return r.content
