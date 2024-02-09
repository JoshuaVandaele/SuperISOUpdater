from functools import cache
from pathlib import Path

import requests

from modules.exceptions import IntegrityCheckError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://gparted.org"
FILE_NAME = "gparted-live-[[VER]]-amd64.iso"


class GPartedLive(GenericUpdater):
    """
    A class representing an updater for GParted Live.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        self.checksum_file: str = requests.get(
            "https://gparted.org/gparted-live/stable/CHECKSUMS.TXT"
        ).text.strip()

    @cache
    def _get_download_link(self) -> str:
        ver = self._version_to_str(self._get_latest_version())
        return f"https://downloads.sourceforge.net/gparted/gparted-live-{GPartedLive._get_gparted_version_style(ver)}-amd64.iso"

    def check_integrity(self) -> bool:
        checksums: list[str] = self.checksum_file.split("###")
        for checksum in checksums:
            if "SHA256" in checksum:
                sha256_sums = checksum
                break
        else:
            raise IntegrityCheckError("Could not find SHA256 sum")

        sha256_hash = parse_hash(sha256_sums, ["amd64.iso"], 0)

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True), sha256_hash
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        # Get last line of the checksum file
        version = self.checksum_file.splitlines()[-1]
        # Get last "word" of the line (Which is the file name)
        version = version.split()[-1]
        # Only keep the version numbers and join them with a dot in between each of them
        version = ".".join(version.split("-")[2:4])

        return self._str_to_version(version)

    @cache
    @staticmethod
    def _get_gparted_version_style(version: str):
        """
        Convert the version string from "x.y.z.a" to "x.y.z-a" format, as used by GParted Live.

        Parameters:
            version (str): The version string in "x.y.z.a" format.

        Returns:
            str: The version string in "x.y.z-a" format.
        """
        return "-".join(version.rsplit(".", 1))
