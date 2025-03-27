from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://enterprise.proxmox.com"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/iso"
FILE_NAME = "proxmox-[[EDITION]]_[[VER]].iso"


class Proxmox(GenericUpdater):
    """
    A class representing an updater for Proxmox.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, edition: str) -> None:
        self.valid_editions = [
            "ve",
            "mail-gateway",
            "backup-server",
        ]
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
                f"Failed to fetch the download page from '{self.download_page.url}'"
            )

        self.soup_download_page = BeautifulSoup(
            self.download_page.content, features="html.parser"
        )

    @cache
    def _get_download_link(self) -> str:
        latest_version_str = self._version_to_str(self._get_latest_version())

        return f"{DOWNLOAD_PAGE_URL}/{FILE_NAME.replace('[[VER]]', latest_version_str).replace("[[EDITION]]", self.edition)}"

    def check_integrity(self) -> bool:
        sha256_url = f"{DOWNLOAD_PAGE_URL}/SHA256SUMS"

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

    def _get_latest_version(self) -> list[str]:
        def parse_version(href: str) -> list[str]:
            return self._str_to_version(href.split("_")[1].split(".iso")[0])

        downloads_list: Tag | None = self.soup_download_page.find("pre")  # type: ignore
        if not downloads_list:
            raise VersionNotFoundError("We were not able to parse the download page")

        download_items = downloads_list.find_all("a")
        if not download_items:
            raise VersionNotFoundError(
                "We were not able to parse the list of download links"
            )

        download_links: list[str] = [
            href
            for download_link in download_items
            if self.edition in (href := download_link.get("href"))
        ]
        if not download_links:
            raise VersionNotFoundError(
                "We were not able to find links for this edition"
            )

        latest_version = []
        for link in download_links:
            version = parse_version(link)
            is_greater_version = self._compare_version_numbers(latest_version, version)
            if is_greater_version:
                latest_version = version

        return latest_version

    def _version_to_str(self, version: list[str]) -> str:
        dash_something: str = version.pop()
        return f"{self.version_splitter.join(str(i) for i in version)}-{dash_something}"

    def _str_to_version(self, version_str: str) -> list[str]:
        version: list[str] = [
            version_number.strip()
            for version_number in version_str.split(self.version_splitter)
        ]
        dash_something: list[str] = version.pop().split("-")
        return version + dash_something
