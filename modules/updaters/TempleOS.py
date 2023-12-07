from functools import cache
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import md5_hash_check, parse_hash

DOMAIN = "https://www.templeos.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/Downloads"
FILE_NAME = "TempleOS_[[EDITION]]_[[VER]].ISO"


class TempleOS(GenericUpdater):
    """
    A class representing an updater for TempleOS.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.
        server_file_name (str): The name of the file to download on the server

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: str, edition: str) -> None:
        self.valid_editions = ["Distro", "Lite"]
        self.edition = edition

        file_path = os.path.join(folder_path, FILE_NAME)
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

        self.server_file_name = (
            f"TempleOS{'Lite' if self.edition == 'Lite' else ''}.ISO"
        )

    @cache
    def _get_download_link(self) -> str:
        return f"{DOWNLOAD_PAGE_URL}/{self.server_file_name}"

    def check_integrity(self) -> bool:
        md5_url = f"{DOWNLOAD_PAGE_URL}/md5sums.txt"

        md5_sums = requests.get(md5_url).text

        md5_sum = parse_hash(md5_sums, [self.server_file_name], 0)

        return md5_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            md5_sum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        file_list_soup: Tag | None = self.soup_download_page.find("pre")  # type: ignore
        if not file_list_soup:
            raise VersionNotFoundError("Could not find download links list")

        page_text = file_list_soup.getText()

        next_line_has_date = False
        date: str | None = None
        for line in page_text.splitlines():
            if self.server_file_name in line:
                next_line_has_date = True
                continue
            if next_line_has_date:
                # Remove last element (size)
                date = " ".join(line.strip().split()[1:-1])
                break
        if not date:
            raise VersionNotFoundError("Could not find date on download page")

        datetime_date = datetime.strptime(date, r"%d-%b-%Y %H:%M")

        return self._str_to_version(str(datetime.timestamp(datetime_date)))
