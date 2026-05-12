import re

import requests_cache
from bs4 import BeautifulSoup

from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp, pgp_receive_key
from modules.Version import Version


class LinuxMint(GenericHTTPMirror):
    # https://linuxmint-installation-guide.readthedocs.io/en/latest/verify.html
    KEY_ID = "27DEB15644C6B3CF3BD7D291300F846BA25BAE09"
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self, edition: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        version = self._determine_latest_version()
        checksum_url: str = f"https://pub.linuxmint.io/stable/{version}/sha256sum.txt"

        super().__init__(
            uri=f"https://pub.linuxmint.io/stable/{version}/",
            download_regex=rf"linuxmint-{version}-{edition}-64bit.iso",
            version=version,
            signed_file=download_file_to_tmp(checksum_url),
        )

    def _determine_latest_version(self) -> Version:
        r = self.session.get(
            "https://pub.linuxmint.io/stable/",
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
