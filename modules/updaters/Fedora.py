from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://fedoraproject.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/spins/[[EDITION]]/download/"
FILE_NAME = "Fedora-[[EDITION]]-Live-x86_64-[[VER]].iso"


class Fedora(GenericUpdater):
    """
    A class representing an updater for Fedora.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, edition: str) -> None:
        self.valid_editions = [
            "Budgie",
            "Cinnamon",
            "KDE",
            "LXDE",
            "MATE_Compiz",
            "SoaS",
            "Sway",
            "Xfce",
            "i3",
        ]
        self.edition = edition

        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        # Make the parameter case insensitive, and find back the correct case using valid_editions
        self.edition = next(
            valid_ed
            for valid_ed in self.valid_editions
            if valid_ed.lower() == self.edition.lower()
        )

        # Weird exception they have
        url_edition = self.edition.lower() if self.edition != "MATE_Compiz" else "mate"

        self.download_page = requests.get(
            DOWNLOAD_PAGE_URL.replace("[[EDITION]]", url_edition)
        )

        if self.download_page.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch the download page from '{self.download_page.url}'"
            )

        self.soup_download_page = BeautifulSoup(
            self.download_page.content, features="html.parser"
        )

    @cache
    def _get_download_link(self) -> str:
        latest_version = self._get_latest_version()
        return f"https://download.fedoraproject.org/pub/fedora/linux/releases/{latest_version[0]}/Spins/x86_64/iso/Fedora-{self.edition}-Live-x86_64-{latest_version[0]}-{latest_version[1]}{'.'+latest_version[2] if len(latest_version)>2 else ''}.iso"

    def check_integrity(self) -> bool:
        latest_version = self._get_latest_version()
        sha256_url = f"https://download.fedoraproject.org/pub/fedora/linux/releases/{latest_version[0]}/Spins/x86_64/iso/Fedora-Spins-{latest_version[0]}-{latest_version[1]}{'.'+latest_version[2] if len(latest_version)>2 else ''}-x86_64-CHECKSUM"

        sha256_sums = requests.get(sha256_url).text

        sha256_sum = parse_hash(sha256_sums, [f"SHA256 (Fedora-{self.edition}"], -1)

        return sha256_hash_check(
            self._get_complete_normalized_file_path(absolute=True),
            sha256_sum,
        )

    @cache
    def _get_latest_version(self) -> list[str]:
        downloads_list: Tag | None = self.soup_download_page.find(
            "div", attrs={"class": "spins-theme"}
        )  # type: ignore
        if not downloads_list:
            raise VersionNotFoundError(
                "We were not able to parse the download categories"
            )

        download_items = downloads_list.find_all(
            "div", attrs={"class": "fp-download-item blue"}
        )
        if not download_items:
            raise VersionNotFoundError(
                "We were not able to parse the list of downloads"
            )

        downloads = next(
            download
            for download in download_items
            if download.find("span", string="Live ISO")
        )
        if not downloads:
            raise VersionNotFoundError(
                "We were not able to parse the Live ISO download item"
            )
        download_a_tag = downloads.find("a", href=True)
        if not download_a_tag:
            raise VersionNotFoundError("We were not able to find the LTS download link")

        return self._str_to_version(
            download_a_tag.get("href")
            .split("x86_64-")[1]
            .split(".iso")[0]
            .replace("-", self.version_splitter)
        )
