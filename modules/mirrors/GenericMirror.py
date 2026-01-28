import logging
import re
import time
from abc import ABC
from pathlib import Path
from urllib.parse import urljoin

import requests
import requests_cache
from bs4 import BeautifulSoup

from modules.exceptions import DownloadLinkNotFoundError, IntegrityCheckError
from modules.SumType import SumType
from modules.utils import (
    blake2b_hash_check,
    blake3_hash_check,
    download_file,
    md5_hash_check,
    parse_hash,
    pgp_check,
    sha1_hash_check,
    sha256_hash_check,
    sha512_hash_check,
)
from modules.Version import Version


class GenericMirror(ABC):
    """
    A class representing a mirror for downloading files.
    This class fetches a web page, determines the type of checksum available,
    and retrieves the checksum value from the page.
    It is intended to be used as a base class for specific mirror implementations.
    """

    CHECKSUM_FILENAMES = {
        SumType.SHA1: ["sha1"],
        SumType.SHA256: ["sha256"],
        SumType.SHA512: ["sha512"],
        SumType.BLAKE2b: ["b2sum", "blake2"],
        SumType.BLAKE3: ["b3sum", "blake3"],
        SumType.MD5: ["md5"],
    }

    SIGNATURE_EXTENSIONS = ["asc", "sig", "gpg"]
    PUBKEY_EXTENSIONS = ["pub", "pem"]

    def __init__(
        self,
        url: str,
        file_regex: str,
        version_regex: str | None = None,
        version_separator: str = ".",
        version_padding: int = 0,
        version: Version | None = None,
        version_class=Version,
        has_signature: bool = True,
        signature_file: Path | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initializes the GenericMirror with a URL and a search regex.

        Args:
            url (str): The URL of the mirror page.
            file_regex (str): A regex pattern to search for the file to download. The regex MUST include the very start and end of the filename.
            version_regex (str, optional): A regex pattern to search for the version on the page. If not provided, the version must be specified with the `version` parameter.
            version_separator (str, optional): The version separator for each component of a version. Used with `version_regex`. Defaults to "."
            version (Version, optional): The version of the file to download. If not provided, it will be determined from the page using `version_regex`.
            has_signature (bool, optional): Should we check for a cryptographic signature. Defaults to True.
            signature_file (Path, optional): File who's signature to check. Defaults to the downloaded file.
            headers (dict[str, str], optional): Headers to pass along for all requests.
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
        self._VersionClass = version_class
        self._has_signature = has_signature
        self._signature_file: Path | None = signature_file
        self.headers: dict[str, str] | None = headers
        self.session = requests_cache.CachedSession(backend="memory")

    @property
    def url(self) -> str:
        return self._url

    @property
    def version_separator(self) -> str:
        return self._version_separator

    def initialize(self) -> None:
        text, soup = self._fetch_page(self._url)
        self._soup_page: BeautifulSoup = soup
        self._text_page: str = text

        self.version: Version = (
            self._determine_version(self._version_regex)
            if self._version_regex
            else self._version
        )  # type: ignore

        self.download_link: str = self._get_download_link()
        types, sums = self._determine_sums()
        self.sum_types: list[SumType] = types
        self.sums: list[str] = sums

        if self._has_signature:
            self.public_key = self._get_public_key()
            self.signature = self._get_signature()

        self.speed: float = self._determine_speed()

    def _checksum_file(self, file: Path) -> bool:
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
                case SumType.BLAKE2b:
                    if not blake2b_hash_check(file, sum):
                        return False
                case SumType.BLAKE3:
                    if not blake3_hash_check(file, sum):
                        return False
        return True

    def _get_public_key(self) -> bytes:
        for url in self._urls():
            if any(url.endswith(ext) for ext in self.PUBKEY_EXTENSIONS):
                r = self.session.get(url)
                r.raise_for_status()
                return r.content
        raise RuntimeError("Could not find a public key")

    def _get_signature(self) -> bytes:
        candidates: list[str] = []
        for url in self._urls():
            if any(url.endswith(ext) for ext in self.SIGNATURE_EXTENSIONS):
                candidates.append(url)

        if not candidates:
            raise RuntimeError("Could not find a signature")

        chosen_url: str = candidates[0]

        urls_with_file_regex = self._urls_with_file_regex()
        for url in candidates:
            if url in urls_with_file_regex:
                chosen_url = url
                if str(self.version) in url:
                    break

        r = self.session.get(chosen_url)
        r.raise_for_status()
        return r.content

    def _signature_check(self, file: Path) -> bool:
        return pgp_check(file, signature=self.signature, public_key=self.public_key)

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

    def _urls_with_file_regex(self) -> list[str]:
        """
        (Protected) Get all URLs from the page that match the regex.

        Returns:
            list[str]: A list of URLs matching the regex.
        """
        return [url for url in self._urls() if re.search(self._file_regex, url)]

    def _urls_with_version(self) -> list[str]:
        """
        (Protected) Get all URLs from the page that contain the version.

        Returns:
            list[str]: A list of URLs containing the version.
        """
        return [url for url in self._urls() if str(self.version) in url]

    def _fetch_page(self, url) -> tuple[str, BeautifulSoup]:
        response = self.session.get(url, headers=self.headers, allow_redirects=True)
        response.raise_for_status()
        return response.text, BeautifulSoup(response.content, features="html.parser")

    def _determine_version_from_search(self, regex, string) -> Version | None:
        version_match = re.search(regex, string)
        if not version_match:
            return None

        return self._VersionClass(
            version_match.group(1), self._version_separator, self._version_padding
        )

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
        latest_version = self._VersionClass("0")
        for url in self._urls_with_file_regex():
            logging.debug(f"Checking URL for version: {url} with regex {version_regex}")
            current_version = self._determine_version_from_search(version_regex, url)
            if current_version and current_version > latest_version:
                latest_version = current_version

        if latest_version == self._VersionClass("0"):
            raise ValueError(
                f"No version found on the page '{self._url}' using regex '{version_regex}'"
            )
        return latest_version

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        def fetch_and_parse_sum() -> tuple[str, int]:
            sum_file = self.session.get(url, headers=self.headers)
            sum_file.raise_for_status()

            sum_file_text = sum_file.text.strip()
            if not re.search(self._file_regex, sum_file_text):
                if not re.search(r"\s", sum_file_text) and len(sum_file_text) > 0:
                    return sum_file_text, 0
                raise ValueError(
                    f"File regex '{self._file_regex}' did not match in sum file text: '{sum_file_text}'"
                )

            sum_pos: int = 1 if re.search(rf"^{self._file_regex}", sum_file_text) else 0
            return sum_file_text, sum_pos

        sums: list[str] = []
        sum_types: list[SumType] = []
        errors: list[str] = []

        for url in self._urls_with_file_regex():
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

                if not re.search(r"\s", sum_file_text):
                    sums.append(sum_file_text)
                else:
                    sums.append(parse_hash(sum_file_text, self._file_regex, sum_pos))
                sum_types.append(sum_type)
        if sum_types and sums:
            return sum_types, sums

        for sum_type, filenames in self.CHECKSUM_FILENAMES.items():
            for url in self._urls():
                for filename in filenames:
                    if filename not in url.lower():
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

        raise ValueError(
            f"Could not determine the sum type from the page at '{self._url}'."
            + (f" Errors: {', '.join(errors)}" if errors else "")
        )

    def _get_download_link(self) -> str:
        """
        (Protected) Get the download link for the latest version of the software.

        Returns:
            str: The download link for the latest version of the software.

        Raises:
            DownloadLinkNotFoundError: If the download link is not found.
        """
        download_links = self._urls_with_file_regex()

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
        with requests.get(
            self.download_link, stream=True, timeout=10, headers=self.headers
        ) as response:
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

    def _download_file(self, file: Path) -> None:
        download_file(self.download_link, file)

    def download_and_verify(self, file: Path) -> bool:
        self._download_file(file)
        # TODO: Better error handling
        checksum_success: bool
        try:
            checksum_success = self._checksum_file(file)
        except Exception:
            checksum_success = False

        if self._has_signature:
            sig_error: str | None = None
            file_to_verify = file if not self._signature_file else self._signature_file
            signature_success: bool
            try:
                signature_success = self._signature_check(file_to_verify)
            except Exception as e:
                signature_success = False
                sig_error = str(e)

            if self._signature_file:
                self._signature_file.unlink()

            if not signature_success:
                if file:
                    file.unlink()
                raise IntegrityCheckError(
                    f"Integrity check failed! (Signature){f': {sig_error}' if sig_error else ''}"
                )

        if not checksum_success:
            if file:
                file.unlink()
            raise IntegrityCheckError("Integrity check failed! (Checksum)")

        return True
