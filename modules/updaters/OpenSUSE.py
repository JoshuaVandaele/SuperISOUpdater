from functools import cache
import os

import requests

from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://download.opensuse.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/download/distribution/leap"
FILE_NAME = "openSUSE-[[EDITION]]-[[VER]]-DVD-x86_64-Current.iso"


class OpenSUSE(GenericUpdater):
    """
    A class representing an updater for OpenSUSE.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: str, edition: str) -> None:
        self.valid_editions = ["leap", "leap-micro", "jump"]
        self.edition = edition.lower()

        file_path = os.path.join(folder_path, FILE_NAME)
        super().__init__(file_path)

    @cache
    def _get_download_link(self) -> str:
        latest_version_str = self._version_to_str(self._get_latest_version())
        return f"{DOWNLOAD_PAGE_URL}/{latest_version_str}/iso/openSUSE-Leap-{latest_version_str}-NET-x86_64-Media.iso"

    def check_integrity(self) -> bool:
        sha256_url = f"{self._get_download_link()}.sha256"

        sha256_sums = requests.get(sha256_url).text

        sha256_sum = parse_hash(sha256_sums, [], 0)

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha256_sum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        r = requests.get(f"{DOWNLOAD_PAGE_URL}?jsontable")

        data = r.json()["data"]

        local_version = self._get_local_version()
        latest = local_version or []

        for i in range(len(data)):
            if "42" in data[i]["name"]:
                continue
            version_number = self._str_to_version(data[i]["name"][:-1])
            if self._compare_version_numbers(latest, version_number):
                latest = version_number

        return latest
