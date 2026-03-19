import re

import requests_cache
from bs4 import BeautifulSoup

from modules.mirrors.GenericMirror import GenericMirror
from modules.utils import create_sig_check_file_from_url, pgp_receive_key
from modules.Version import Version


class Kernel(GenericMirror):
    KEY_ID = "27DEB15644C6B3CF3BD7D291300F846BA25BAE09"
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self, edition: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        version = self._determine_version()
        checksum_url: str = (
            f"https://mirrors.edge.kernel.org/linuxmint/stable/{version}/sha256sum.txt"
        )

        super().__init__(
            url=f"https://mirrors.edge.kernel.org/linuxmint/stable/{version}/",
            file_regex=rf"linuxmint-{version}-{edition}-64bit.iso",
            version=version,
            signature_file=create_sig_check_file_from_url(checksum_url),
        )

    def _determine_version(self) -> Version:
        r = self.session.get(
            "https://mirrors.edge.kernel.org/linuxmint/stable/",
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features="html.parser")
        urls = [str(a_tag.get("href")) for a_tag in soup.find_all("a", href=True)]

        latest_version = Version("0")
        for url in urls:
            ver_match = re.match(r"^(\d[\d\.]+)", url)
            if not ver_match:
                continue
            current_version = Version(ver_match.group(0))
            if current_version and current_version > latest_version:
                latest_version = current_version

        if latest_version == Version("0"):
            raise ValueError(f"No version found on the page '{self._url}'")
        return latest_version

    def _get_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
