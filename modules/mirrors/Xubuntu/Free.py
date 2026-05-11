import re

import requests_cache
from bs4 import BeautifulSoup

from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp, pgp_receive_key
from modules.Version import Version


class Free(GenericHTTPMirror):
    KEY_ID = "843938DF228D22F7B3742BC0D94AA3F0EFE21092"
    KEY_SERVER = "keyserver.ubuntu.com"

    def __init__(self, arch: str, edition: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        version = self._determine_latest_version()
        checksum_url: str = f"http://ftp.free.fr/mirrors/ftp.xubuntu.com/releases/{version}/release/SHA256SUMS"

        super().__init__(
            uri=f"http://ftp.free.fr/mirrors/ftp.xubuntu.com/releases/{version}/release/",
            download_regex=rf"xubuntu-{version}-{edition}-{arch}.iso",
            version=version,
            signed_file=download_file_to_tmp(checksum_url),
        )

    def _determine_latest_version(self) -> Version:
        r = self.session.get(
            "http://ftp.free.fr/mirrors/ftp.xubuntu.com/releases/",
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features="html.parser")
        urls = [str(a_tag.get("href")) for a_tag in soup.find_all("a", href=True)]

        latest_version = Version("0")
        for url in urls:
            ver_match = re.match(r"^([\d\.]+)\/?$", url)
            if not ver_match:
                continue
            current_version = Version(ver_match.group(1))
            if current_version and current_version > latest_version:
                latest_version = current_version

        if latest_version == Version("0"):
            raise ValueError(f"No version found on the page '{self.uri}'")
        return latest_version

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
