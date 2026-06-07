import re

import requests_cache
from bs4 import BeautifulSoup

from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp, pgp_receive_key
from modules.Version import Version


class MirrorService(GenericHTTPMirror):
    KEY_ID = "843938DF228D22F7B3742BC0D94AA3F0EFE21092"
    KEY_SERVER = "keyserver.ubuntu.com"

    def __init__(self, flavor: str, arch: str, edition: str) -> None:
        self.flavor = flavor
        self.session = requests_cache.CachedSession(backend="memory")
        version = self._determine_latest_version()
        checksum_url: str = f"https://www.mirrorservice.org/sites/cdimage.ubuntu.com/cdimage/{self.flavor}/releases/{version}/release/SHA256SUMS"

        super().__init__(
            uri=f"https://www.mirrorservice.org/sites/cdimage.ubuntu.com/cdimage/{self.flavor}/releases/{version}/release/",
            download_regex=rf"{self.flavor}-{version}-{edition}-{arch}.iso",
            version=version,
            signed_file=download_file_to_tmp(checksum_url),
        )

    def _determine_latest_version(self) -> Version:
        ver_r = self.session.get(
            f"https://www.mirrorservice.org/sites/cdimage.ubuntu.com/cdimage/{self.flavor}/releases/",
        )
        ver_r.raise_for_status()
        ver_soup = BeautifulSoup(ver_r.content, features="html.parser")
        ver_urls = [
            str(a_tag.get("href")) for a_tag in ver_soup.find_all("a", href=True)
        ]

        latest_version = Version("0")
        for ver_url in ver_urls:
            ver_match = re.match(r"^([\d\.]+)\/?$", ver_url)
            if not ver_match:
                continue
            current_version = Version(ver_match.group(1))
            if current_version:
                # Need to filter out pre-releases
                rel_r = self.session.get(
                    f"https://www.mirrorservice.org/sites/cdimage.ubuntu.com/cdimage/{self.flavor}/releases/{current_version}/",
                )
                rel_r.raise_for_status()
                rel_soup = BeautifulSoup(rel_r.content, features="html.parser")
                rel_urls = [
                    str(a_tag.get("href"))
                    for a_tag in rel_soup.find_all("a", href=True)
                ]

                for rel_url in rel_urls:
                    if rel_url == "release/" and current_version > latest_version:
                        latest_version = current_version

        if latest_version == Version("0"):
            raise ValueError(f"No version found on the page '{ver_r.url}'")
        return latest_version

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
