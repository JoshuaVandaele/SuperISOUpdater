from functools import cache
from urllib.parse import urljoin

from modules.Checksum import Checksum, SHA256Sum
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import parse_hash


class RockyLinux(GenericHTTPMirror):
    def __init__(self, arch: str, edition: str) -> None:
        super().__init__(
            uri="https://download.rockylinux.org/pub/rocky/",
            download_regex=rf"Rocky-([\d.]+)-{edition}-{arch}(.+)?\.iso",
            version_regex=rf"Rocky-([\d.]+)-{edition}-{arch}(.+)?\.iso",
            has_signature=False,
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
        return [SHA256Sum(parse_hash(lines, self._download_regex, -1))]
