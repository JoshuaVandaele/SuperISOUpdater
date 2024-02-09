from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://geo.mirror.pkgbuild.com"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/iso/latest"
FILE_NAME = "archlinux-[[VER]]-x86_64.iso"


class ArchLinux(GenericUpdater):
    """
    A class representing an updater for Arch Linux.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        self.download_page = requests.get(DOWNLOAD_PAGE_URL)

        if self.download_page.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch the download page from '{DOWNLOAD_PAGE_URL}'"
            )

        self.soup_download_page = BeautifulSoup(
            self.download_page.content, features="html.parser"
        )

    @cache
    def _get_download_link(self) -> str:
        latest_version_str = self._version_to_str(self._get_latest_version())
        return f"{DOWNLOAD_PAGE_URL}/{FILE_NAME.replace('[[VER]]', latest_version_str)}"

    def check_integrity(self) -> bool:
        sha256_url = "https://geo.mirror.pkgbuild.com/iso/latest/sha256sums.txt"

        sha256_sums = requests.get(sha256_url).text

        sha256_sum = parse_hash(
            sha256_sums,
            [str(self._get_complete_normalized_file_path(absolute=False))],
            0,
        )

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha256_sum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        download_a_tags = self.soup_download_page.find_all("a", href=True)
        if not download_a_tags:
            raise VersionNotFoundError("We were not able to parse the download page")
        download_a_tag = next(
            a_tag for a_tag in download_a_tags if "archlinux" in a_tag.get("href")
        )
        if not download_a_tag:
            raise VersionNotFoundError("We were not able to parse the download links")

        return self._str_to_version(download_a_tag.getText().split("-")[1])
