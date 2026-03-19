import re
import tempfile
from pathlib import Path

import requests_cache
from bs4 import BeautifulSoup

from modules.mirrors.GenericMirror import GenericMirror
from modules.utils import pgp_receive_key
from modules.Version import Version


class OVH(GenericMirror):
    KEY_ID = "843938DF228D22F7B3742BC0D94AA3F0EFE21092"
    KEY_SERVER = "keyserver.ubuntu.com"

    def create_sig_check_file(self) -> Path:
        r = self.session.get(self.checksum_url)
        r.raise_for_status()

        sig_file = tempfile.NamedTemporaryFile(delete=False, prefix="sisou_", mode="wb")
        sig_file.write(r.content)
        sig_file.flush()
        sig_file.close()

        return Path(tempfile.gettempdir()) / sig_file.name

    def __init__(self, arch: str, edition: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        version = self._determine_version()
        self.checksum_url: str = (
            f"https://ubuntu.mirrors.ovh.net/releases/{version}/SHA256SUMS"
        )

        super().__init__(
            url=f"https://ubuntu.mirrors.ovh.net/releases/{version}/",
            file_regex=rf"ubuntu-{version}-{edition}-{arch}.iso",
            version=version,
            signature_file=self.create_sig_check_file(),
        )

    def _determine_version(self) -> Version:
        r = self.session.get(
            "https://ubuntu.mirrors.ovh.net/releases/",
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features="html.parser")
        urls = [str(a_tag.get("href")) for a_tag in soup.find_all("a", href=True)]

        latest_version = Version("0")
        for url in urls:
            ver_match = re.match(r"^((\d+\.)+\d+)", url)
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
