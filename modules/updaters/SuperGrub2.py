import zipfile
from functools import cache
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from modules.exceptions import (
    DownloadLinkNotFoundError,
    IntegrityCheckError,
    VersionNotFoundError,
)
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import download_file, parse_hash, sha256_hash_check

DOMAIN = "https://www.supergrubdisk.org"
DOWNLOAD_PAGE_URL = f"{DOMAIN}/category/download/supergrub2diskdownload/"
FILE_NAME = "SuperGrub2-[[VER]].img"


class SuperGrub2(GenericUpdater):
    """
    A class representing an updater for SuperGrub2.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        self.download_page = requests.get(DOWNLOAD_PAGE_URL)

        if self.download_page.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch the download page from '{DOWNLOAD_PAGE_URL}'"
            )

        self.soup_download_page = BeautifulSoup(
            self.download_page.content, features="html.parser"
        )

        self.soup_latest_download_article: Tag = self.soup_download_page.find("article")  # type: ignore
        if not self.soup_latest_download_article:
            raise DownloadLinkNotFoundError(
                "Could not find the article containing download information"
            )

    @cache
    def _get_download_link(self) -> str:
        download_tag = self._find_in_table("Download supergrub2")

        if not download_tag:
            raise DownloadLinkNotFoundError(
                "We were not able to find the link to the SourceForge in the table"
            )

        href_attributes = download_tag.find_all(href=True)

        if not href_attributes:
            raise DownloadLinkNotFoundError("No download link found in the `Tag`")

        sourceforge_url = href_attributes[0].get("href")
        return sourceforge_url

    def check_integrity(self, archive_to_check: Path) -> bool:
        sha256_sums_tag = self.soup_latest_download_article.find_all("pre")
        if not sha256_sums_tag:
            raise IntegrityCheckError("Couldn't find the SHA256 sum")
        sha256_sums_tag = sha256_sums_tag[-1]
        sha256_checksums_str = sha256_sums_tag.getText()
        sha_256_checksum: str = parse_hash(
            sha256_checksums_str,
            [
                f"supergrub2-{self._get_latest_version()[0]}",
                ".img.zip",
            ],
            0,
        )

        return sha256_hash_check(archive_to_check, sha_256_checksum)

    def install_latest_version(self) -> None:
        download_link: str = self._get_download_link()

        new_file = self._get_complete_normalized_file_path(absolute=True)

        archive_path = new_file.with_suffix(".zip")

        download_file(download_link, archive_path)

        local_file = self._get_local_file()

        if not self.check_integrity(archive_path):
            archive_path.unlink()
            raise IntegrityCheckError("Integrity check failed")

        with zipfile.ZipFile(archive_path) as z:
            file_list = z.namelist()
            iso = next(file for file in file_list if file.endswith(".img"))
            extracted_file = Path(z.extract(iso, path=new_file.parent))

        if local_file:
            local_file.unlink()
        archive_path.unlink()

        try:
            extracted_file.rename(new_file)
        except FileExistsError:
            # On Windows, files are not overwritten by default, so we need to remove the old file first
            new_file.unlink()
            extracted_file.rename(new_file)

    @cache
    def _get_latest_version(self) -> list[str]:
        download_table: Tag | None = self.soup_latest_download_article.find("table", attrs={"cellpadding": "5px"})  # type: ignore
        if not download_table:
            raise VersionNotFoundError(
                "We were not able to find the table of download which contains the version number"
            )

        download_table_header: Tag | None = download_table.find("h2")  # type: ignore
        if not download_table_header:
            raise VersionNotFoundError(
                "We were not able to find the header containing the version number"
            )

        header: str = download_table_header.getText().lower()
        return self._str_to_version(
            header.replace("super grub2 disk", "")
            .strip()  # Parse from "Super Grub2 Disk 2.06s2-beta1"
            .replace("s", self.version_splitter)
            .replace("-beta", self.version_splitter)
        )

    def _find_in_table(self, row_name_contains: str) -> Tag | None:
        """
        Find the HTML Tag containing specific information in the download page table.

        Args:
            row_name_contains (str): A string that identifies the row in the table.

        Returns:
            Tag | None: The HTML Tag containing the desired information, or None .
        """
        download_table: Tag | None = self.soup_latest_download_article.find("table", attrs={"cellpadding": "5px"})  # type: ignore

        if not download_table:
            raise LookupError("Could not find the table with download information")

        for tr in download_table.find_all("tr"):
            for td in tr.find_all("td"):
                if row_name_contains in td.getText():
                    return td
        return None
