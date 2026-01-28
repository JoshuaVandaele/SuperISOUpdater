import re
from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from modules.exceptions import DownloadLinkNotFoundError, VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://alpinelinux.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/downloads/"
DOWNLOAD_CDN_URL = "https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64"
FILE_NAME = "alpine-[[EDITION]]-[[VER]]-x86_64.iso"


class AlpineLinux(GenericUpdater):
    """
    A class representing an updater for Arch Linux.

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
            "standard",
            "extended",
            "virt",
            "xen",
        ]
        self.edition = edition.lower()

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

    def _get_download_link(self) -> str:
        return f"{DOWNLOAD_CDN_URL}/{self._get_complete_normalized_file_path(absolute=False)}"

    def check_integrity(self) -> bool:
        sha256_url = f"{self._get_download_link()}.sha256"

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
        version_tag = self.soup_download_page.find(
            "strong", text=re.compile(r"\d+\.\d+\.\d+")
        )

        if not version_tag:
            raise VersionNotFoundError(
                "We were not able to find a version number on the download page"
            )

        return self._str_to_version(version_tag.getText())
