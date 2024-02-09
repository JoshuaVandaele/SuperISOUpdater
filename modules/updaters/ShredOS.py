from functools import cache
from pathlib import Path

from modules.updaters.GenericUpdater import GenericUpdater
from modules.updaters.util_update_checker import (
    github_get_latest_version,
    parse_github_release,
)
from modules.utils import parse_hash, sha1_hash_check

FILE_NAME = " shredos-[[VER]].img "


class ShredOS(GenericUpdater):
    """
    A class representing an updater for ShredOS.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        release = github_get_latest_version("PartialVolume", "shredos.x86_64")

        self.release_info = parse_github_release(release)

    @cache
    def _get_download_link(self) -> str:
        return next(
            download_link
            for filename, download_link in self.release_info["files"].items()
            if filename.endswith(".img") and "x86-64" in filename
        )

    def check_integrity(self) -> bool:
        sha1_sums = self.release_info["text"]

        sha1_sum = parse_hash(
            sha1_sums,
            [
                "sha1",
                self._version_to_str(self._get_latest_version()),
                "x86-64",
                ".img",
            ],
            1,
        )

        return sha1_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha1_sum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        version = self.release_info["tag"]

        start_index = version.find("v")
        end_index = version.find("_")

        version = version[start_index + 1 : end_index]

        return self._str_to_version(version)
