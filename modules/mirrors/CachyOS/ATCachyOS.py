import re

import requests_cache
from bs4 import BeautifulSoup

from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import pgp_receive_key
from modules.Version import Version


class ATCachyOS(GenericHTTPMirror):
    KEY_ID = "F3B607488DB35A47"
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self, edition: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        self.edition = edition
        version = self._determine_latest_version()

        super().__init__(
            uri=f"https://at.cachyos.org/ISO/{edition}/{version}/",
            download_regex=rf"cachyos-{edition}-linux-{version}.iso",
            version=version,
            version_separator="",
        )

    def _determine_latest_version(self) -> Version:
        r = self.session.get(
            f"https://at.cachyos.org/ISO/{self.edition}/",
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features="html.parser")
        urls = [str(a_tag.get("href")) for a_tag in soup.find_all("a", href=True)]

        latest_version = Version("0", separator="")
        for url in urls:
            ver_match = re.match(r"^.\/(\d+)\/$", url)
            if not ver_match:
                continue
            current_version = Version(ver_match.group(1), separator="")
            if current_version and current_version > latest_version:
                latest_version = current_version

        if latest_version == Version("0", separator=""):
            raise ValueError(f"No version found on the page '{r.url}'")
        return latest_version

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
