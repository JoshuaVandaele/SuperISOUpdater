from functools import cache
from pathlib import Path

import requests

from modules.updaters.GenericUpdater import GenericUpdater
from modules.updaters.util_update_checker import (
    github_get_latest_version,
    parse_github_release,
)
from modules.utils import parse_hash, sha256_hash_check

FILE_NAME = "rescuezilla-[[VER]]-64bit.[[EDITION]].iso"


class Rescuezilla(GenericUpdater):
    """
    A class representing an updater for Rescuezilla.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        release_info (dict): Github release information

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, edition: str) -> None:
        self.valid_editions = ["focal", "jammy", "lunar", "mantic", "noble"]
        self.edition = edition.lower()

        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        release = github_get_latest_version("rescuezilla", "rescuezilla")

        self.release_info = parse_github_release(release)

    @cache
    def _get_download_link(self) -> str:
        return self.release_info["files"][
            str(self._get_complete_normalized_file_path(absolute=False))
        ]

    def check_integrity(self) -> bool:
        sha256_url = self.release_info["files"]["SHA256SUM"]

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
        return self._str_to_version(self.release_info["tag"])
