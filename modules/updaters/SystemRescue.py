from functools import cache
import os
import re

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from modules.exceptions import DownloadLinkNotFoundError, VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://www.system-rescue.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/Download"
FILE_NAME = "systemrescue-[[VER]]-amd64.iso"


class SystemRescue(GenericUpdater):
    """
    A class representing an updater for SystemRescue.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: str) -> None:
        """
        Initialize a SystemRescue updater object.

        Args:
            folder_path (str): The path to the folder where the SystemRescue file is stored.

        Raises:
            ConnectionError: If the download page cannot be fetched successfully.
        """
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
        download_tag: Tag | None = self._find_in_table("Fastly")

        if not download_tag:
            raise DownloadLinkNotFoundError(
                "Failed to find the `Tag` containing the download link"
            )

        href_attributes = download_tag.find_all(href=True)
        if not href_attributes:
            raise DownloadLinkNotFoundError("No download link found in the `Tag`")

        return href_attributes[0].get("href")

    def check_integrity(self) -> bool:
        version_str = self._version_to_str(self._get_latest_version())
        sha256_download_link = f"{DOMAIN}/releases/{version_str}/systemrescue-{version_str}-amd64.iso.sha256"

        r = requests.get(sha256_download_link)
        sha256_checksum = parse_hash(
            r.text,
            [self._get_normalized_file_path(False, self._get_latest_version())],
            0,
        )

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha256_checksum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        download_link = self._get_download_link()

        latest_version_regex = re.search(
            r"releases\/(.+)\/",  # Parse from https://fastly-cdn.system-rescue.org/releases/10.01/systemrescue-10.01-amd64.iso
            download_link,
        )

        if latest_version_regex:
            return self._str_to_version(latest_version_regex.group(1))

        raise VersionNotFoundError("Could not find the latest available version")

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
        s: Tag | None = self.soup_download_page.find("div", attrs={"id": "colcenter"})  # type: ignore

        if not s:
            raise LookupError(
                "Could not find the div containing the table with download information"
            )

        s = s.find("table")  # type: ignore

        if not s:
            raise LookupError(
                "Could not find the table containing download information"
            )

        for tr in s.find_all("tr"):
            for td in tr.find_all("td"):
                if row_name_contains in td.getText():
                    return td

        raise LookupError(f"Failed to find '{row_name_contains}' in the table")
