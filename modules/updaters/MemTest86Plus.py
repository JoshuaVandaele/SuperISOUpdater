import zipfile
from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from modules.exceptions import (
    DownloadLinkNotFoundError,
    IntegrityCheckError,
    VersionNotFoundError,
)
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import download_file, parse_hash, sha256_hash_check

DOMAIN = "https://www.memtest.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}"
FILE_NAME = "Memtest86plus-[[VER]].iso"


class MemTest86Plus(GenericUpdater):
    """
    A class representing an updater for MemTest86+.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.
        soup_download_card (Tag): The specific HTML Tag containing the download information card.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path) -> None:
        """
        Initialize the MemTest86Plus updater.

        Args:
            folder_path (str): The path to the folder where the MemTest86+ ISO file is stored.

        Raises:
            ConnectionError: If the download page could not be fetched successfully.
            DownloadLinkNotFoundError: If the card containing download information is not found.
        """
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
        self.soup_download_card: Tag = self.soup_download_page.find(
            "div", attrs={"class": "col-xxl-4"}
        )  # type: ignore

        if not self.soup_download_card:
            raise DownloadLinkNotFoundError(
                "Could not find the card containing download information"
            )

    @cache
    def _get_download_link(self) -> str:
        download_element: Tag | None = self.soup_download_card.find("a", string="Linux ISO (64 bits)")  # type: ignore
        if not download_element:
            raise DownloadLinkNotFoundError("Could not find the download link")
        return f"{DOWNLOAD_PAGE_URL}{download_element.get('href')}"

    def check_integrity(self) -> bool:
        """
        Check the integrity of the downloaded file by verifying its SHA-256 hash against the one provided on the website.

        Returns:
            bool: True if the integrity check passes, False otherwise.
        """
        version_str = self._version_to_str(self._get_latest_version())
        sha_256_url = f"{DOWNLOAD_PAGE_URL}/download/v{version_str}/sha256sum.txt"
        sha_256_checksums_str: str = requests.get(sha_256_url).text
        sha_256_checksum: str = parse_hash(sha_256_checksums_str, ["64.iso"], 0)

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True).with_suffix(".zip"),
            sha_256_checksum,
        )

    def install_latest_version(self) -> None:
        """
        Download and install the latest version of the software.

        Raises:
            ValueError: If no download link is available for the latest version.
            IntegrityCheckError: If the integrity check of the downloaded file fails.
        """
        download_link = self._get_download_link()

        new_file = self._get_complete_normalized_file_path(absolute=True)

        archive_path = new_file.with_suffix(".zip")

        download_file(download_link, archive_path)

        local_file = self._get_local_file()

        if not self.check_integrity():
            archive_path.unlink()
            raise IntegrityCheckError("Integrity check failed")

        with zipfile.ZipFile(archive_path) as z:
            file_list = z.namelist()
            iso = next(file for file in file_list if file.endswith(".iso"))
            extracted_file = Path(z.extract(iso, path=new_file.parent))

        if local_file:
            local_file.unlink()
        archive_path.unlink()

        try:
            extracted_file.rename(new_file)
        except FileExistsError:
            # On Windows, files are not overwritten by default, so we need to remove the old file first
            new_file.unlink()
            extracted_file.rename(new_file)

    @cache
    def _get_latest_version(self) -> list[str]:
        card_title: Tag | None = self.soup_download_card.find(
            "span", attrs={"class": "text-primary fs-2"}
        )  # type: ignore

        if not card_title:
            raise VersionNotFoundError("Could not find the latest version")

        return self._str_to_version(
            card_title.getText().split("v")[-1]  # Parse from Memtest86+ v 0.0
        )
