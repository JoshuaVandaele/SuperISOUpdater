import re

import requests_cache
from bs4 import BeautifulSoup

from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.Version import Version


class NetBSDCDN(GenericHTTPMirror):
    def __init__(self, arch: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        version = self._determine_latest_version()

        super().__init__(
            uri=f"https://cdn.netbsd.org/pub/NetBSD/images/{version}/",
            download_regex=rf"NetBSD-{version}-{arch}.iso",
            version=version,
            has_signature=False,
        )

    def _determine_latest_version(self) -> Version:
        r = self.session.get(
            "https://cdn.netbsd.org/pub/NetBSD/images/",
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

    def _fetch_and_parse_sum(self, url: str) -> tuple[str, int]:
        min_sum_text, _ = super()._fetch_and_parse_sum(url)
        return min_sum_text, -1
