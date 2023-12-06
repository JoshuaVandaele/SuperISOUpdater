from functools import cache
import os

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from modules.exceptions import DownloadLinkNotFoundError, VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import sha256_hash_check

DOMAIN = "https://www.hirensbootcd.org/"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/download"
FILE_NAME = "HBCD_PE_[[VER]]_x64.iso"


class HirensBootCDPE(GenericUpdater):
    """
    A class representing an updater for Hiren's Boot CD PE.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

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

    @cache
    def _get_download_link(self) -> str:
        download_tag: Tag | None = self._find_in_table("Filename")

        if not download_tag:
            raise DownloadLinkNotFoundError(
                "Failed to find the `Tag` containing the download link"
            )

        href_attributes = download_tag.find_all(href=True)
        if not href_attributes:
            raise DownloadLinkNotFoundError("No download link found in the `Tag`")

        return href_attributes[0].get("href")

    def check_integrity(self) -> bool:
        """
        Check the integrity of the downloaded file by verifying its SHA-256 hash against the one provided on the website.

        Returns:
            bool: True if the integrity check passes, False otherwise.

        Raises:
            LookupError: If the SHA-256 hash or its container Tag is not found in the download page.
        """
        sha256_tag: Tag | None = self._find_in_table("SHA-256")

        if not sha256_tag:
            raise LookupError("Failed to find the `Tag` containing the SHA-256 value")

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True), sha256_tag.getText()
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        s: Tag | None = self.soup_download_page.find(
            "div", attrs={"class": "post-content"}
        )  # type: ignore
        if not s:
            raise VersionNotFoundError(
                "Could not find the div containing version information"
            )

        s = s.find("span")  # type: ignore
        if not s:
            raise VersionNotFoundError(
                "Could not find the span containing the version information"
            )

        return self._str_to_version(
            s.getText()
            .split("(v")[1]  # Parse from Hiren’s BootCD PE x64 (v1.0.2) – ISO Content
            .split(")")[0]
        )

    def _find_in_table(self, row_name_contains: str) -> Tag | None:
        """
        Find the HTML Tag containing specific information in the download page table.

        Args:
            row_name_contains (str): A string that identifies the row in the table.

        Returns:
            Tag | None: The HTML Tag containing the desired information, or None if not found.

        Raises:
            LookupError: If the table or the specified row_name_contains is not found in the download page.
        """
        s: Tag | None = self.soup_download_page.find("div", attrs={"class": "table-1"})  # type: ignore

        if not s:
            raise LookupError(
                "Could not find the table containing download information"
            )

        next_is_result = False
        for tr in s.find_all("tr"):
            for td in tr.find_all("td"):
                if next_is_result:
                    return td
                if row_name_contains in td.getText():
                    next_is_result = True

        raise LookupError(f"Failed to find '{row_name_contains}' in the table")
