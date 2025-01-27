from functools import cache
from pathlib import Path

import logging

import re
import requests

from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://download.opensuse.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/download/tumbleweed/iso"
FILE_NAME = "openSUSE-[[EDITION]]-x86_64-[[VER]].iso"


class OpenSUSERolling(GenericUpdater):
    """
    A class representing an updater for OpenSUSE.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, edition: str) -> None:
        self.valid_editions = ["MicroOS-DVD", "Tumbleweed-DVD", "Tumbleweed-NET", "Tumbleweed-GNOME-Live", "Tumbleweed-KDE-Live", "Tumbleweed-XFCE-Live", "Tumbleweed-Rescue-CD"]
        self.edition = edition

        self.download_page_url = DOWNLOAD_PAGE_URL
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

    def _capitalize_edition(self) -> str:
        for capEdition in self.valid_editions:
            if capEdition.lower() is self.edition.lower():
                return capEdition
        # shouldn't get here
        return self.edition

    @cache
    def _get_download_link(self) -> str:
        isoFile = FILE_NAME.replace("[[EDITION]]", self._capitalize_edition()).replace("[[VER]]","Current")
        return f"{self.download_page_url}/{isoFile}"


    def check_integrity(self) -> bool:
        sha256_url = f"{self._get_download_link()}.sha256"

        sha256_sums = requests.get(sha256_url).text

        sha256_sum = parse_hash(sha256_sums, [], 0)

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha256_sum,
        )

    def _get_latest_version(self) -> list[str]:
        sha256_url = f"{self._get_download_link()}.sha256"
        sha256_sums = requests.get(sha256_url).text
        return self._str_to_version(sha256_sums.split(" ")[-1])

    def _str_to_version(self, version_str: str):
        version = "0"
        pattern = r'^.*Snapshot(\d*)-.*$'

        match = re.search(pattern, version_str)
        if match:
            version = match.group(1)

        logging.debug(
            f"[OpenSUSERolling._parse_version] parsing:{version_str}, found version:{version}"
        )
        return [version]

    def _version_to_str(self, version):
        return f"Snapshot{version[0]}-Media"
