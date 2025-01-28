from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import sha256_hash_check
from modules.WindowsConsumerDownload import WindowsConsumerDownloader

DOMAIN = "https://www.microsoft.com"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/en-us/software-download/windows11"
FILE_NAME = "Win11_[[VER]]_EnglishInternational_x64v2.iso"


class Windows11(GenericUpdater):
    """
    A class representing an updater for Windows 11.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, lang: str) -> None:
        self.valid_langs = [
            "Arabic",
            "Brazilian Portuguese",
            "Bulgarian",
            "Chinese",
            "Chinese",
            "Croatian",
            "Czech",
            "Danish",
            "Dutch",
            "English",
            "English International",
            "Estonian",
            "Finnish",
            "French",
            "French Canadian",
            "German",
            "Greek",
            "Hebrew",
            "Hungarian",
            "Italian",
            "Japanese",
            "Korean",
            "Latvian",
            "Lithuanian",
            "Norwegian",
            "Polish",
            "Portuguese",
            "Romanian",
            "Russian",
            "Serbian Latin",
            "Slovak",
            "Slovenian",
            "Spanish",
            "Spanish (Mexico)",
            "Swedish",
            "Thai",
            "Turkish",
            "Ukrainian",
        ]
        self.lang = lang
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
        # Make the parameter case insensitive, and find back the correct case using valid_editions
        self.lang = next(
            valid_lang
            for valid_lang in self.valid_langs
            if valid_lang.lower() == self.lang.lower()
        )
        self.version_splitter = "H"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "referer": "folfy.blue",
        }

        self.download_page = requests.get(DOWNLOAD_PAGE_URL, headers=self.headers)

        if self.download_page.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch the download page from '{DOWNLOAD_PAGE_URL}'"
            )

        self.soup_download_page = BeautifulSoup(
            self.download_page.content, features="html.parser"
        )

        self.hash: str | None = None

    @cache
    def _get_download_link(self) -> str:
        return WindowsConsumerDownloader.windows_consumer_download("11", self.lang)

    def check_integrity(self) -> bool:
        if not self.hash:
            return False

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            WindowsConsumerDownloader.windows_consumer_file_hash("11", self.lang),
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        header: Tag | None = self.soup_download_page.find("div", class_="row").find("div").find("p", string=lambda text: "Version" in text)  # type: ignore
        if not header:
            raise VersionNotFoundError(
                "Could not find header containing version information"
            )

        return [
            version_number.strip()
            for version_number in header.getText()
            .split("Version")[1]
            .replace(")", "")
            .split("H")
        ]
