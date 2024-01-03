from functools import cache
import os
import zipfile

import requests

from modules.exceptions import IntegrityCheckError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import download_file, sha1_hash_check

DOMAIN = "https://dl.google.com"
FILE_NAME = "chromeos_[[VER]]_[[EDITION]].img"


class ChromeOS(GenericUpdater):
    """
    A class representing an updater for ChromeOS.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        chromium_releases_info (list[dict]): List of release info for each edition
        cur_edition_info: Release info for the selected edition

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: str, edition: str) -> None:
        self.valid_editions = ["ltc", "ltr", "stable"]
        self.edition = edition.lower()

        file_path = os.path.join(folder_path, FILE_NAME)
        super().__init__(file_path)

        self.chromium_releases_info: list[dict] = requests.get(
            f"{DOMAIN}/dl/edgedl/chromeos/recovery/cloudready_recovery2.json"
        ).json()

        self.cur_edition_info: dict = next(
            d
            for d in self.chromium_releases_info
            if d["channel"].lower() == self.edition
        )

    @cache
    def _get_download_link(self) -> str:
        return self.cur_edition_info["url"]

    def check_integrity(self) -> bool:
        sha1_sum = self.cur_edition_info["sha1"]

        return sha1_hash_check(
            self._get_complete_normalized_file_path(absolute=True) + ".zip",
            sha1_sum,
        )

    def install_latest_version(self) -> None:
        """
        Download and install the latest version of the software.

        Raises:
            IntegrityCheckError: If the integrity check of the downloaded file fails.
        """
        download_link = self._get_download_link()

        new_file = self._get_complete_normalized_file_path(absolute=True)

        archive_path = f"{new_file}.zip"

        local_file = self._get_local_file()

        download_file(download_link, archive_path)

        try:
            integrity_check = self.check_integrity()
        except Exception as e:
            raise IntegrityCheckError(
                "Integrity check failed: An error occurred"
            ) from e

        if not integrity_check:
            os.remove(archive_path)
            raise IntegrityCheckError("Integrity check failed: Hashes do not match")

        with zipfile.ZipFile(archive_path) as z:
            file_list = z.namelist()

            file_ext = "bin"
            to_extract = next(
                file for file in file_list if file.lower().endswith(file_ext)
            )

            extracted_file = z.extract(to_extract, path=os.path.dirname(new_file))
        os.rename(extracted_file, new_file)

        os.remove(archive_path)
        if local_file:
            os.remove(local_file)  # type: ignore

    @cache
    def _get_latest_version(self) -> list[str]:
        return self._str_to_version(self.cur_edition_info["version"])
