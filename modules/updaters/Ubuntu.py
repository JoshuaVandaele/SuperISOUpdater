from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://releases.ubuntu.com"
DOWNLOAD_PAGE_URL = f"{DOMAIN}"
FILE_NAME = "ubuntu-[[EDITION]]-[[VER]]-desktop-amd64.iso"


class Ubuntu(GenericUpdater):
    """
    A class representing an updater for Ubuntu.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, edition: str) -> None:
        self.valid_editions = ["LTS", "Interim"]
        self.edition = edition

        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        # Make the parameter case insensitive, and find back the correct case using valid_editions
        self.edition = next(
            valid_ed
            for valid_ed in self.valid_editions
            if valid_ed.lower() == self.edition.lower()
        )

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
        return f"{DOMAIN}/{latest_version_str}/{f'ubuntu-{latest_version_str}-desktop-amd64.iso'}"

    def check_integrity(self) -> bool:
        latest_version_str = self._version_to_str(self._get_latest_version())

        sha256_url = f"{DOWNLOAD_PAGE_URL}/{latest_version_str}/SHA256SUMS"

        sha256_sums = requests.get(sha256_url).text

        sha256_sum = parse_hash(
            sha256_sums, [f"ubuntu-{latest_version_str}-desktop-amd64.iso"], 0
        )

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha256_sum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        download_categories = self.soup_download_page.find_all(
            "div", attrs={"class": "col-4"}
        )
        if not download_categories:
            raise VersionNotFoundError(
                "We were not able to parse the download categories"
            )
        downloads = next(
            download_category
            for download_category in download_categories
            if download_category.find("h4", string=f"{self.edition} Releases")
        )
        if not downloads:
            raise VersionNotFoundError(
                f"We were not able to parse the {self.edition} downloads"
            )
        latest = downloads.find("a", href=True)
        if not latest:
            raise VersionNotFoundError(
                f"We were not able to find {self.edition} downloads"
            )
        # This is `x.y`, however to get `x.y.z` we need to go to `/x.y`
        xy_version = latest.getText().split()[1]

        version_page = requests.get(f"{DOWNLOAD_PAGE_URL}/{xy_version}")

        soup_version_page = BeautifulSoup(version_page.content, features="html.parser")

        title = soup_version_page.find("title")

        if not title:
            raise VersionNotFoundError(
                "We were not able to find the title of the version page"
            )

        title_text = title.getText()

        # Extract version from string "Ubuntu x.y.z (Name of Release)"
        return self._str_to_version(title_text.split()[1])
