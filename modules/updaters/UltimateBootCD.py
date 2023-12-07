from functools import cache
import os
from random import shuffle

import requests
from bs4 import BeautifulSoup, Tag

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://www.ultimatebootcd.com"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/download.html"
MIRRORS = [
    "https://mirror.clientvps.com/ubcd",
    "http://mirror.koddos.net/ubcd",
    "https://mirror.lyrahosting.com/ubcd",
]
FILE_NAME = "ubcd[[VER]].iso"


class UltimateBootCD(GenericUpdater):
    """
    A class representing an updater for Ultimate Boot CD.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.
        mirrors (list[str])
        mirror (str)
        download_table (Tag)

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: str) -> None:
        file_path = os.path.join(folder_path, FILE_NAME)
        super().__init__(file_path)

        self.download_page = requests.get(DOWNLOAD_PAGE_URL)

        if self.download_page.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch the download page from '{DOWNLOAD_PAGE_URL}'"
            )

        self.soup_download_page = BeautifulSoup(
            self.download_page.content, features="html.parser"
        )

        self.mirrors = MIRRORS
        shuffle(self.mirrors)

        self.download_table: Tag | None = None
        for mirror in self.mirrors:
            self.mirror_page = requests.get(mirror)

            if self.mirror_page.status_code != 200:
                continue

            self.soup_mirror_page = BeautifulSoup(
                self.mirror_page.content, features="html.parser"
            )

            self.download_table = self.soup_mirror_page.find("table")  # type: ignore
            if self.download_table:
                self.mirror = mirror
                break

        if not self.mirror_page:
            raise ConnectionError(f"Could not connect to any mirrors!")

        if not self.download_table:
            raise LookupError(f"Could not find table of downloads in any mirrors")

    @cache
    def _get_download_link(self) -> str:
        latest_version: list[str] = self._get_latest_version()
        return f"{self.mirror}/ubcd{self._version_to_str(latest_version)}.iso"

    def check_integrity(self) -> bool:
        nowrap_tds: list[Tag] = self.soup_download_page.find_all(
            "td", attrs={"nowrap": "true"}
        )

        tts: list[Tag] = next(td.find_all("tt") for td in nowrap_tds if td.find("tt"))

        sha256_sum: str = next(
            parse_hash(tt.getText(), [], -1) for tt in tts if "SHA-256" in tt.getText()
        )

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True), sha256_sum
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        download_a_tags = self.download_table.find_all("a", href=True)  # type: ignore
        if not download_a_tags:
            raise VersionNotFoundError("We were not able to parse the download page")

        versions_href = [
            href
            for a_tag in download_a_tags
            if FILE_NAME.split("[[VER]]")[0] in (href := a_tag.get("href"))
            and (href.endswith(".iso"))
        ]

        version = 0
        for version_href in versions_href:
            version_href_number = int("".join(filter(str.isdigit, version_href)))
            if version_href_number > version:
                version = version_href_number

        return self._str_to_version(str(version))
