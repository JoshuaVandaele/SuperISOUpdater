from functools import cache
from pathlib import Path

import logging
import re
import glob

import requests
from bs4 import BeautifulSoup

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import sha256_hash_check

import bz2

DOMAIN = "https://pkg.opnsense.org/releases/mirror"
DOWNLOAD_PAGE_URL = f"{DOMAIN}"
FILE_NAME = "OPNsense-[[VER]]-[[EDITION]]-amd64.[[FILE_TYPE]].bz2"


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

        if self.edition == "dvd":
            self.file_type = "iso"
        else:
            self.file_type = "img"

        file_path = folder_path / FILE_NAME.replace("[[FILE_TYPE]]", self.file_type)
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
        return f"{DOWNLOAD_PAGE_URL}/{self._get_complete_normalized_file_path(absolute=False)}"

    def check_integrity(self) -> bool:
        latest_version_str = self._version_to_str(self._get_latest_version())

        sha256_url = f"{DOMAIN}/OPNsense-{latest_version_str}-checksums-amd64.sha256"

        sha256_sums = requests.get(sha256_url).text

        sha256_sum = self._extract_hash(sha256_sums, str(self._get_complete_normalized_file_path(absolute=False)))

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha256_sum,
        )

    def install_latest_version(self) -> None:
        super().install_latest_version()
        # extract bz2, taken from https://stackoverflow.com/questions/16963352/decompress-bz2-files
        logging.info(f"Extracting {str(self._get_complete_normalized_file_path(absolute=False))}")
        path = str(self._get_complete_normalized_file_path(absolute=True))
        zipfile = bz2.BZ2File(path) # open the file
        data = zipfile.read() # get the decompressed data
        newfilepath = path[:-4] # assuming the filepath ends with .bz2
        open(newfilepath, 'wb').write(data) # write a uncompressed file
        logging.info("Extraction finished. Deleting the compressed file.")
        Path.unlink(self._get_complete_normalized_file_path(absolute=True))


    def _extract_hash(self, sha256_sums: str, title: str):
        lines = sha256_sums.splitlines()
        for line in lines:
            parts = line.split(" ")
            if title == parts[1].replace('(', '').replace(')', ''):
                return parts[-1]
        return ""

    @cache
    def _get_latest_version(self) -> list[str]:
        download_a_tags = self.soup_download_page.find_all("a", href=True)
        if not download_a_tags:
            raise VersionNotFoundError("We were not able to parse the download page")

        local_version = self._get_local_version()
        latest = local_version or []

        for a_tag in download_a_tags:
            href = a_tag.get("href")
            if not "OPNsense" in href:
                continue
            version_number = self._str_to_version(href[:-1])
            if self._compare_version_numbers(latest, version_number):
                latest = version_number

        return latest

    def _get_local_file(self) -> Path | None:
        """
        Get the path of the locally stored file that matches the filename pattern.

        Returns:
            str | None: The path of the locally stored file if found, None if no file exists.
        """
        file_path = self._get_normalized_file_path(
            absolute=True,
            version=None,
            edition=self.edition if self.has_edition() else None,  # type: ignore
            lang=self.lang if self.has_lang() else None,  # type: ignore
        )

        local_files = glob.glob(str(file_path).replace("[[VER]]", "*").replace('.bz2',''))

        if local_files:
            return Path(local_files[0])
        logging.debug(
            f"[GenericUpdater._get_local_file] No local file found for {self.__class__.__name__}"
        )
        return None

    def _str_to_version(self, version_str: str):
        version = "0"
        pattern = r'^(OPNsense-)?(\d+\.\d).*$'

        match = re.search(pattern, version_str)
        if match:
            version = match.group(2)

        return [version]

    @staticmethod
    def _compare_version_numbers(
        old_version: list[str], new_version: list[str]
    ) -> bool:
        """
        Compare version numbers to check if a new version is available.

        Args:
            old_version (list[str]): The old version as a list of version components.
            new_version (list[str]): The new version as a list of version components.

        Returns:
            bool: True if the new version is greater than the old version, False otherwise.
        """
        for i in range(len(new_version)):
            try:
                if float(new_version[i]) > float(old_version[i]):
                    return True
            except ValueError:
                if float(new_version[i]) > float(old_version[i]):
                    return True
            except IndexError:
                return True
        return False
