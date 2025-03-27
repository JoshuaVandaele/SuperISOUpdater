import bz2
import re
from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://pkg.opnsense.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/releases/mirror"
FILE_NAME = "OPNsense-[[VER]]-[[EDITION]]-amd64.[[EXT]]"


class OPNsense(GenericUpdater):
    """
    A class representing an updater for OPNsense.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, edition: str) -> None:
        self.valid_editions = ["dvd", "nano", "serial", "vga"]
        self.edition = edition.lower()

        file_extension = "iso" if self.edition == "dvd" else "img"

        file_path = folder_path / FILE_NAME.replace("[[EXT]]", file_extension)
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
        return f"{DOWNLOAD_PAGE_URL}/{self._get_complete_normalized_file_path(absolute=False)}.bz2"

    def check_integrity(self) -> bool:
        latest_version_str = self._version_to_str(self._get_latest_version())

        sha256_url = (
            f"{DOWNLOAD_PAGE_URL}/OPNsense-{latest_version_str}-checksums-amd64.sha256"
        )

        sha256_sums = requests.get(sha256_url).text

        sha256_sum = parse_hash(
            sha256_sums,
            [self.edition],
            -1,
        )

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha256_sum,
        )

    def install_latest_version(self) -> None:
        super().install_latest_version()
        bz2_path = self._get_complete_normalized_file_path(absolute=True).with_suffix(
            ".bz2"
        )

        if bz2_path.exists():
            bz2_path.unlink()

        self._get_complete_normalized_file_path(absolute=True).rename(bz2_path)

        bz2_file = bz2.BZ2File(bz2_path)
        data = bz2_file.read()

        extracted_filepath = bz2_path.with_suffix(self.file_path.suffix)
        with open(extracted_filepath, "wb") as new_file:
            new_file.write(data)

        bz2_path.unlink()

    @cache
    def _get_latest_version(self) -> list[str]:
        download_a_tags = self.soup_download_page.find_all("a", href=True)
        if not download_a_tags:
            raise VersionNotFoundError("We were not able to parse the download page")

        local_version = self._get_local_version()
        latest = local_version or []

        for a_tag in download_a_tags:
            href = a_tag.get("href")
            if not self.edition in href:
                continue
            version_number = self._str_to_version(href.split("-")[1])
            if self._compare_version_numbers(latest, version_number):
                latest = version_number

        return latest
