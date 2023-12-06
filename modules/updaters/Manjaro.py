from functools import cache
import os
import re

import requests

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha512_hash_check

DOMAIN = "https://gitlab.manjaro.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/web/iso-info/-/raw/master/file-info.json"
FILE_NAME = "manjaro-[[EDITION]]-[[VER]]-linux61.iso"


class Manjaro(GenericUpdater):
    """
    A class representing an updater for Manjaro.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        file_info_json (dict[Any, Any]): JSON file containing file information for each edition

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: str, edition: str) -> None:
        self.valid_editions = [
            "plasma",
            "xfce",
            "gnome",
            "budgie",
            "cinnamon",
            "i3",
            "sway",
            "mate",
        ]
        self.edition = edition.lower()
        file_path = os.path.join(folder_path, FILE_NAME)
        super().__init__(file_path)

        self.file_info_json = requests.get(DOWNLOAD_PAGE_URL).json()
        self.file_info_json["releases"] = (
            self.file_info_json["official"] | self.file_info_json["community"]
        )

    @cache
    def _get_download_link(self) -> str:
        return self.file_info_json["releases"]["plasma"]["image"]

    def check_integrity(self) -> bool:
        sha512_url = self.file_info_json["releases"]["plasma"]["checksum"]

        sha512_sums = requests.get(sha512_url).text

        sha512_sum = parse_hash(sha512_sums, [], 0)

        return sha512_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha512_sum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        download_link = self._get_download_link()

        latest_version_regex = re.search(
            r"kde\/(.+)\/",  # Parse from https://fastly-cdn.system-rescue.org/releases/10.01/systemrescue-10.01-amd64.iso
            download_link,
        )

        if latest_version_regex:
            return self._str_to_version(latest_version_regex.group(1))

        raise VersionNotFoundError("Could not find the latest available version")
