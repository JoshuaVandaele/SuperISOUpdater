import logging
import re
import time
from abc import ABC
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from modules.exceptions import DownloadLinkNotFoundError
from modules.SumType import SumType
from modules.utils import (
    md5_hash_check,
    parse_hash,
    sha1_hash_check,
    sha256_hash_check,
    sha512_hash_check,
)
from modules.Version import Version

CHECKSUM_FILENAMES = {
    SumType.SHA1: "SHA1SUMS",
    SumType.SHA1: "sha1sums.txt",
    SumType.SHA256: "SHA256SUMS",
    SumType.SHA256: "sha256sums.txt",
    SumType.SHA512: "SHA512SUMS",
    SumType.SHA512: "sha512sums.txt",
    SumType.MD5: "MD5SUMS",
    SumType.MD5: "md5sums.txt",
}


class GenericMirror(ABC):
    """
    A class representing a mirror for downloading files.
    This class fetches a web page, determines the type of checksum available,
    and retrieves the checksum value from the page.
    It is intended to be used as a base class for specific mirror implementations.
    """

    def __init__(
        self,
        url: str,
        file_regex: str,
        version_regex: str | None = None,
        version_separator: str = ".",
        version_padding: int = 0,
        version: Version | None = None,
    ) -> None:
        """
        Initializes the GenericMirror with a URL and a search regex.

        Args:
            url (str): The URL of the mirror page.
            file_regex (str): A regex pattern to search for the file to download. The regex MUST include the very start and end of the file name.
            version_regex (str, optional): A regex pattern to search for the version on the page. If not provided, the version must be specified with the `version` parameter.
            version_separator (str, optional): The version separator for each component of a version. Used with `version_regex`. Defaults to "."
            version (Version, optional): The version of the file to download. If not provided, it will be determined from the page using `version_regex`.
        """
        if not version_regex and not version:
            raise ValueError(
                "Either 'version_regex' or 'version' must be provided to determine the version."
            )
        self._url: str = url
        self._file_regex: str = file_regex
        self._version_regex: str | None = version_regex
        self._version_separator: str = version_separator
        self._version_padding: int = version_padding
        self._version: Version | None = version

    @property
    def url(self) -> str:
        return self._url

    @property
    def version_separator(self) -> str:
        return self._version_separator

    def initialize(self) -> None:
        text, soup = self._fetch_page()
        self._soup_page: BeautifulSoup = soup
        self._text_page: str = text

        print(r"self._determine_version(self._version_regex)")
        self.version: Version = (
            self._determine_version(self._version_regex)
            if self._version_regex
            else self._version
        )  # type: ignore

        print(r"types, sums = self._determine_sums()")
        types, sums = self._determine_sums()
        self.sum_types: list[SumType] = types
        self.sums: list[str] = sums
        print(r"self.download_link: str = self._get_download_link()")
        self.download_link: str = self._get_download_link()
        print(r"self.speed: float = self._determine_speed()")
        self.speed: float = self._determine_speed()

    def checksum_file(self, file: Path) -> bool:
        for sum, sum_type in zip(self.sums, self.sum_types):
            match sum_type:
                case SumType.MD5:
                    if not md5_hash_check(file, sum):
                        return False
                case SumType.SHA1:
                    if not sha1_hash_check(file, sum):
                        return False
                case SumType.SHA256:
                    if not sha256_hash_check(file, sum):
                        return False
                case SumType.SHA512:
                    if not sha512_hash_check(file, sum):
                        return False
        return True

    def _urls(self) -> list[str]:
        """
        (Protected) Get all URLs from the page.

        Returns:
            list[str]: A list of URLs found on the page.
        """
        results: list[str] = []
        for a_tag in self._soup_page.find_all("a", href=True):
            url = a_tag.get("href")
            if url.startswith("http"):
                results.append(url)
            else:
                results.append(urljoin(self._url, url))
        return results

    def _urls_with_regex(self) -> list[str]:
        """
        (Protected) Get all URLs from the page that match the regex.

        Returns:
            list[str]: A list of URLs matching the regex.
        """
        return [url for url in self._urls() if re.search(self._file_regex, url)]

    def _fetch_page(self) -> tuple[str, BeautifulSoup]:
        response = requests.get(self._url)
        response.raise_for_status()
        return response.text, BeautifulSoup(response.content, features="html.parser")

    def _determine_version(self, version_regex: str) -> Version:
        """
        (Protected) Determine the version from the page using the provided regex.

        Args:
            version_regex (str): The regex pattern to search for the version.

        Returns:
            str: The determined version.

        Raises:
            ValueError: If no version is found on the page.
        """
        latest_version = Version("0")
        for url in self._urls_with_regex():
            logging.debug(f"Checking URL for version: {url} with regex {version_regex}")
            version_match = re.search(version_regex, url)
            if not version_match:
                continue

            current_version = Version(
                version_match.group(1), self._version_separator, self._version_padding
            )
            if current_version > latest_version:
                latest_version = current_version

        if latest_version == Version("0"):
            raise ValueError(
                f"No version found on the page '{self._url}' using regex '{version_regex}'"
            )
        return latest_version

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        def fetch_and_parse_sum() -> tuple[str, int]:
            sum_file = requests.get(url)
            if sum_file.status_code != 200:
                raise ConnectionError(
                    f"Failed to fetch sum file from '{url}' with status code {sum_file.status_code}"
                )

            sum_file_text = sum_file.text.strip()
            if not re.search(self._file_regex, sum_file_text):
                raise ValueError(
                    f"File regex '{self._file_regex}' did not match in sum file text: '{sum_file_text}'"
                )

            sum_pos: int = 1 if re.search(rf"^{self._file_regex}", sum_file_text) else 0
            return sum_file_text, sum_pos

        sums: list[str] = []
        sum_types: list[SumType] = []
        errors: list[str] = []

        for url in self._urls_with_regex():
            if str(self.version) not in url:
                continue
            for sum_type in SumType:
                if not re.search(rf"{sum_type.value}", url):
                    continue

                try:
                    sum_file_text, sum_pos = fetch_and_parse_sum()
                except Exception as e:
                    errors.append(
                        f"Error fetching or parsing sum file from '{url}': {e}"
                    )
                    continue

                sums.append(parse_hash(sum_file_text, self._file_regex, sum_pos))
                sum_types.append(sum_type)
        if sum_types and sums:
            return sum_types, sums

        for sum_type in SumType:
            if sum_type in CHECKSUM_FILENAMES:
                for url in self._urls():
                    if CHECKSUM_FILENAMES[sum_type] in url:
                        try:
                            sum_file_text, sum_pos = fetch_and_parse_sum()
                        except Exception as e:
                            errors.append(
                                f"Error fetching or parsing sum file from '{url}': {e}"
                            )
                            continue

                        sums.append(
                            parse_hash(sum_file_text, self._file_regex, sum_pos)
                        )
                        sum_types.append(sum_type)
        if sum_types and sums:
            return sum_types, sums

        raise ValueError(
            f"Could not determine the sum type from the page at '{self._url}'."
            + f" Errors: {', '.join(errors)}"
            if errors
            else ""
        )

    def _get_download_link(self) -> str:
        """
        (Protected) Get the download link for the latest version of the software.

        Returns:
            str: The download link for the latest version of the software.

        Raises:
            DownloadLinkNotFoundError: If the download link is not found.
        """
        download_links = self._urls_with_regex()

        for link in download_links:
            if re.search(rf"{self._file_regex}$", link) and str(self.version) in link:
                return link

        raise DownloadLinkNotFoundError(
            f"Download link not found for regex '{self._file_regex}' and version '{self.version}' on page '{self._url}'"
        )

    def _determine_speed(self, probe_bytes: int = 2048) -> float:
        """
        (Protected) Determine the download speed of the mirror.

        Args:
            probe_bytes (int): The number of bytes to download for speed testing. Default is 2048 bytes.

        Returns:
            float: The download speed.
        """
        with requests.get(self.download_link, stream=True, timeout=10) as response:
            response.raise_for_status()
            start = time.time_ns()
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                total_size += len(chunk)
                if total_size >= probe_bytes:
                    break
            end = time.time_ns()

        elapsed_time = end - start
        if elapsed_time == 0:
            return float("inf")
        return total_size / elapsed_time
