import re

import requests_cache
from bs4 import BeautifulSoup

from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.Version import Version


class FreeBSD(GenericHTTPMirror):
    def __init__(self, arch: str, edition: str) -> None:
        match arch:
            case "amd64":
                parent_arch = "amd64"
            case "aarch64":
                parent_arch = "arm64"
            case "powerpc64":
                parent_arch = "powerpc"
            case "powerpc64le":
                parent_arch = "powerpc"
            case "riscv64":
                parent_arch = "riscv"
            case _:
                raise ValueError(f"Unsupported architecture '{arch}'")

        self.arch = arch
        self.edition = edition
        self.parent_arch = parent_arch
        arch_file_part = f"{parent_arch}-{arch}" if parent_arch != arch else arch

        self.session = requests_cache.CachedSession(backend="memory")
        self.version = self._determine_latest_version()

        super().__init__(
            uri=f"https://download.freebsd.org/releases/{self.parent_arch}/{self.arch}/ISO-IMAGES/{self.version}/",
            download_regex=rf"FreeBSD-{self.version}-RELEASE-{arch_file_part}-{self.edition}\.iso",
            version=self.version,
            # FIXME: There is a signed checksum file, but importing https://docs.freebsd.org/pgpkeys/pgpkeys.txt with gpg fails due to signatures being corrupted.
            # Even trying to use the (partially) working keys fails to verify the signatures.
            # https://docs.freebsd.org/en/books/handbook/pgpkeys/
            # https://www.freebsd.org/releases/{version}R/signatures/
            has_signature=False,
        )

    def _determine_latest_version(self) -> Version:
        r = self.session.get(
            f"https://download.freebsd.org/releases/{self.parent_arch}/{self.arch}/",
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features="html.parser")
        urls = [str(a_tag.get("href")) for a_tag in soup.find_all("a", href=True)]

        latest_version = Version("0")
        for url in urls:
            ver_match = re.match(r"^([\d\.]+)-RELEASE\/?$", url)
            if not ver_match:
                continue
            current_version = Version(ver_match.group(1))
            if current_version and current_version > latest_version:
                latest_version = current_version

        if latest_version == Version("0"):
            raise ValueError(f"No version found on the page '{r.url}'")
        return latest_version

    def _fetch_and_parse_sum(self, url: str) -> tuple[str, int]:
        min_sum_text, _ = super()._fetch_and_parse_sum(url)
        return min_sum_text, -1
