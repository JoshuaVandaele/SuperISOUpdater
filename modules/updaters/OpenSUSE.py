from functools import cache
from pathlib import Path

import requests

from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import parse_hash, sha256_hash_check

DOMAIN = "https://download.opensuse.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/download/distribution/[[EDITION]]"
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

    def __init__(self, folder_path: Path, edition: str) -> None:
        self.valid_editions = ["leap", "leap-micro", "jump"]
        self.edition = edition.lower()

        self.download_page_url = DOWNLOAD_PAGE_URL.replace("[[EDITION]]", self.edition)

        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

    def _capitalize_edition(self) -> str:
        return "-".join([s.capitalize() for s in self.edition.split("-")])

    @cache
    def _get_download_link(self) -> str:
        latest_version_str = self._version_to_str(self._get_latest_version())
        url = f"{self.download_page_url}/{latest_version_str}"

        edition_page = requests.get(f"{url}?jsontable").json()["data"]

        if any("product" in item["name"] for item in edition_page):
            url += "/product"
        
        if self.edition != "leap-micro":
            latest_version_str += "-NET"

        return f"{url}/iso/openSUSE-{self._capitalize_edition()}-{latest_version_str}-x86_64{"-Current" if self.edition != "leap-micro" else ""}.iso"

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
        r = requests.get(f"{self.download_page_url}?jsontable")

        data = r.json()["data"]

        local_version = self._get_local_version()
        latest = local_version or []

        for i in range(len(data)):
            if "42" in data[i]["name"]:
                continue
            version_number = self._str_to_version(data[i]["name"][:-1])
            if self._compare_version_numbers(latest, version_number):
                sub_r = requests.get(f"{self.download_page_url}/{self._version_to_str(version_number)}?jsontable")
                sub_data = sub_r.json()["data"]
                if not any("iso" in item["name"] or "product" in item["name"] for item in sub_data):
                    continue
                
                latest = version_number

        return latest
