from functools import cache
import os

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from modules.updaters.GenericUpdater import GenericUpdater
from urllib.parse import urljoin

from modules.utils import md5_hash_check, parse_hash

DOMAIN = "https://www.hdat2.com"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/download.html"
FILE_NAME = "HDAT2_[[EDITION]]_[[VER]].[[EXT]]"


class HDAT2(GenericUpdater):
    """
    A class representing an updater for HDAT2.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: str, edition: str) -> None:
        self.valid_editions = ["full", "lite", "diskette"]
        self.edition = edition.lower()

        if self.edition == "diskette":
            extension = "IMG"
        else:
            extension = "ISO"

        self.file_name = FILE_NAME.replace("[[EXT]]", extension)

        file_path = os.path.join(folder_path, self.file_name)
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
        version_str = self._version_to_str(self._get_latest_version())
        match self.edition:
            case "full":
                soup = self._find_in_table([version_str], ["LITE", "IMG", "EXE"])
            case "lite":
                soup = self._find_in_table([version_str, "LITE"], ["IMG", "EXE"])
            case "diskette":
                soup = self._find_in_table([version_str, "HDAT2IMG"], ["ISO", "EXE"])
            case _:
                raise NotImplementedError(
                    f"Edition {self.edition} is not implemented yet."
                )

        a_tag = soup.find("a", href=True)

        if not a_tag:
            raise LookupError("Could not find HTML tag containing download link")

        return urljoin(DOMAIN, a_tag["href"])  # type: ignore

    def check_integrity(self) -> bool:
        version_str = self._version_to_str(self._get_latest_version())
        match self.edition:
            case "full":
                soup = self._find_in_table([version_str], ["LITE"])
            case "lite":
                soup = self._find_in_table([version_str, "LITE"])
            case "diskette":
                soup = self._find_in_table([version_str, "HDAT2IMG"])
            case _:
                raise NotImplementedError(
                    f"Edition {self.edition} is not implemented yet."
                )
        tag_with_hash = soup.find(lambda tag: "MD5=" in tag.text)
        if not tag_with_hash:
            raise LookupError("Could not find HTML tag containing MD5 hash")

        md5_sum = parse_hash(tag_with_hash.text, ["MD5=", version_str], -1).replace(
            "MD5=", ""
        )

        return md5_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            md5_sum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        version_tag = self.soup_download_page.find("font", {"color": "blue"})

        if not version_tag:
            raise LookupError(
                "Could not find the HTML tag containing the version number"
            )

        version_text = version_tag.get_text(strip=True)

        return self._str_to_version(
            version_text.split()[2]  # Get 'x.y' from 'Latest version x.y date'
        )

    def _find_in_table(
        self,
        row_name_contains: list[str],
        row_name_doesnt_contain: list[str] | None = None,
    ) -> Tag:
        """
        Find the HTML Tag containing specific information in the download page table.

        Args:
            row_name_contains (list[str]): Strings that identify the row in the table.
            row_name_doesnt_contain (list[str]): Strings that shouldn't be in the row

        Returns:
            Tag: The HTML Tag containing the desired information, or None if not found.

        Raises:
            LookupError: If the table or the specified row_name_contains is not found in the download page.
        """
        if not row_name_doesnt_contain:
            row_name_doesnt_contain = []
        s: Tag | None = self.soup_download_page.find("table", attrs={"bgcolor": "#B3B3B3"})  # type: ignore

        if not s:
            raise LookupError(
                "Could not find the table containing download information"
            )

        for tr in s.find_all("tr"):
            text = tr.getText()
            if any(string in text for string in row_name_doesnt_contain):
                continue
            if all(string in text for string in row_name_contains):
                return tr

        raise LookupError(f"Failed to find value in the table")
