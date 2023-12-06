from functools import cache
import glob
import os
import re
import zipfile

import requests
from bs4 import BeautifulSoup

from modules.exceptions import IntegrityCheckError, VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import download_file, parse_hash, sha256_hash_check

DOMAIN = "https://www.ibiblio.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/pub/micro/pc-stuff/freedos/files/distributions/"
FILE_NAME = "FreeDOS-[[VER]]-[[EDITION]].[[EXT]]"


class FreeDOS(GenericUpdater):
    """
    A class representing an updater for FreeDOS.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: str, edition: str) -> None:
        self.valid_editions = [
            "BonusCD",
            "FloppyEdition",
            "FullUSB",
            "LegacyCD",
            "LiteUSB",
            "LiveCD",
        ]

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

    @cache
    def _get_download_link(self) -> str:
        latest_version = self._get_latest_version()
        latest_version_str = self._version_to_str(latest_version)
        return f"{DOWNLOAD_PAGE_URL}/{latest_version_str}/official/FD{''.join(latest_version)}-{self.edition}.zip"

    def check_integrity(self) -> bool:
        checksums_url = "https://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/distributions/1.3/official/verify.txt"

        checksums = requests.get(checksums_url).text

        try:
            sha256_sums = next(
                sums for sums in checksums.split("\n\n") if "sha256" in sums
            )
        except StopIteration as e:
            raise IntegrityCheckError(
                "Could not find the sha256 hash in the hash list file"
            ) from e

        sha256_sum = parse_hash(sha256_sums, [self.edition], 0)

        return sha256_hash_check(
            self._get_normalized_file_path(
                True, self._get_latest_version(), self.edition
            ).replace("[[EXT]]", "zip"),
            sha256_sum,
        )

    def install_latest_version(self) -> None:
        """
        Download and install the latest version of the software.

        Raises:
            IntegrityCheckError: If the integrity check of the downloaded file fails.
        """
        download_link = self._get_download_link()

        new_file = self._get_complete_normalized_file_path(absolute=True)
        archive_path = new_file.replace("[[EXT]]", "zip")

        local_file = self._get_local_file()

        download_file(download_link, archive_path)

        try:
            integrity_check = self.check_integrity()
        except IntegrityCheckError as e:
            raise e
        except Exception as e:
            raise IntegrityCheckError(
                "Integrity check failed: An error occurred"
            ) from e

        if not integrity_check:
            os.remove(archive_path)
            raise IntegrityCheckError("Integrity check failed: Hashes do not match")

        with zipfile.ZipFile(archive_path) as z:
            file_list = z.namelist()
            try:
                file_ext = "ISO"
                to_extract = next(
                    file for file in file_list if file.upper().endswith(file_ext)
                )
            except StopIteration:
                file_ext = "IMG"
                to_extract = next(
                    file for file in file_list if file.upper().endswith(file_ext)
                )

            extracted_file = z.extract(to_extract, path=os.path.dirname(new_file))
        os.rename(extracted_file, new_file.replace("[[EXT]]", file_ext))

        os.remove(archive_path)
        if local_file:
            os.remove(local_file)  # type: ignore

    def _get_local_file(self) -> str | None:
        file_path = self._get_normalized_file_path(
            absolute=True,
            version=None,
            edition=self.edition,
        )

        local_files = glob.glob(
            file_path.replace("[[VER]]", "*").replace("[[EXT]]", "*")
        )

        if local_files:
            return local_files[0]
        return None

    @cache
    def _get_latest_version(self) -> list[str]:
        download_a_tags = self.soup_download_page.find_all("a", href=True)
        if not download_a_tags:
            raise VersionNotFoundError("We were not able to parse the download page")

        latest_version = self._get_local_version()
        version_regex = re.compile(r"^(([0-9]+)(\.?))+$")
        for a_tag in download_a_tags:
            href = a_tag.get("href")
            version: str = href[:-1]
            if version_regex.fullmatch(version):
                compared_version = self._str_to_version(version)
                if latest_version:
                    if self._compare_version_numbers(latest_version, compared_version):
                        latest_version = compared_version
                else:
                    latest_version = compared_version

        if not latest_version:
            raise VersionNotFoundError("Could not find a valid version")

        return latest_version
