from functools import cache
from pathlib import Path
from random import shuffle

import requests
from bs4 import BeautifulSoup, Tag

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import md5_hash_check, parse_hash

MIRRORS = [
    "https://mirror.clientvps.com/ubcd",
    "http://mirror.koddos.net/ubcd"
]
FILE_NAME = "ubcd[[VER]].iso"


class UltimateBootCD(GenericUpdater):
    """
    A class representing an updater for Ultimate Boot CD.

    Attributes:
        mirrors (list[str])
        mirror (str)
        download_table (Tag)

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        self.mirrors = MIRRORS
        shuffle(self.mirrors)

        self.download_table: Tag | None = None
        for mirror in self.mirrors:
            mirror_page = requests.get(mirror)

            if mirror_page.status_code != 200:
                continue

            soup_mirror_page = BeautifulSoup(
                mirror_page.content, features="html.parser"
            )

            self.download_table = soup_mirror_page.find("table")  # type: ignore
            if self.download_table:
                self.mirror = mirror
                break

        if not self.download_table:
            raise ConnectionError(f"Could not connect to any mirrors or find download table!")

    @cache
    def _get_download_link(self) -> str:
        latest_version: list[str] = self._get_latest_version()
        return f"{self.mirror}/ubcd{self._version_to_str(latest_version)}.iso"

    def check_integrity(self) -> bool:
        latest_version = self._get_latest_version()
        iso_name = f"ubcd{self._version_to_str(latest_version)}.iso"
        md5_url = f"{self.mirror}/{iso_name}.md5"
        md5_response = requests.get(md5_url)
        if md5_response.status_code != 200:
            raise ConnectionError(f"Failed to fetch MD5 checksum from '{md5_url}'")
        md5_sum = parse_hash(md5_response.text, [], 0)
        return md5_hash_check(
            self._get_complete_normalized_file_path(absolute=True), md5_sum
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
