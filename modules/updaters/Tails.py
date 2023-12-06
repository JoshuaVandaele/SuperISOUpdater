import os

import requests
from bs4 import BeautifulSoup

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import pgp_check
from functools import cache


DOMAIN = "https://mirrors.edge.kernel.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/tails/stable"
FILE_NAME = "tails-amd64-[[VER]].iso"
PUB_KEY_URL = "https://tails.net/tails-signing.key"


class Tails(GenericUpdater):
    """
    A class representing an updater for Linux Mint.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
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
        latest_version_str = self._version_to_str(self._get_latest_version())
        return f"{DOWNLOAD_PAGE_URL}/tails-amd64-{latest_version_str}/{self._get_complete_normalized_file_path(absolute=False)}"

    def check_integrity(self) -> bool:
        sig_url = f"{self._get_download_link()}.sig"

        sig = requests.get(sig_url).content
        pub_key = requests.get(PUB_KEY_URL).content

        return pgp_check(
            self._get_complete_normalized_file_path(absolute=True), sig, pub_key
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        download_a_tags = self.soup_download_page.find_all("a", href=True)
        if not download_a_tags:
            raise VersionNotFoundError("We were not able to parse the download page")

        local_version = self._get_local_version()
        latest = local_version or []

        for a_tag in download_a_tags:
            href = a_tag.get("href")
            if not "tails-amd64" in href:
                continue
            version = href.split("-")[-1]
            if not version[0].isnumeric():
                continue
            version_number = self._str_to_version(version[:-1])
            if self._compare_version_numbers(latest, version_number):
                latest = version_number

        return latest
