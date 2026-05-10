import logging
import re
import time
from pathlib import Path
from typing import Callable, Self
from urllib.parse import urljoin

import requests
import requests_cache
from bs4 import BeautifulSoup

from modules.Checksum import Checksum, SumType
from modules.exceptions import DownloadLinkNotFoundError
from modules.mirrors.GenericMirror import GenericMirror
from modules.utils import download_file, parse_hash
from modules.Version import Version


class GenericHTTPMirror(GenericMirror):
    _init_steps: list[str] = [
        "_init_soup",
        "_init_version",
        "_init_download_link",
        "_init_checksums",
        "_init_signature",
        "_init_speed",
    ]

    SIGNATURE_EXTENSIONS = ["asc", "sig", "gpg"]
    PUBKEY_EXTENSIONS = ["key", "pub", "pem"]

    def __init__(
        self,
        uri: str,
        download_regex: str,
        headers: dict[str, str] | None = None,
        version: Version | None = None,
        version_regex: str | None = None,
        version_class: type[Version] = Version,
        version_separator: str = ".",
        version_padding: int = 0,
        has_signature: bool = True,
        signed_file: Path | Callable[[Self], Path] | None = None,
    ) -> None:
        if not version_regex and not version:
            raise ValueError(
                "Either 'version_regex' or 'version' must be provided to determine the version."
            )
        super().__init__(
            uri,
            version_class,
            version_separator,
            version_padding,
            has_signature,
            signed_file,
        )
        self._download_regex: str = download_regex
        self._version_regex: str | None = version_regex
        self.version: Version | None = version
        self.headers: dict[str, str] | None = headers
        self.session = requests_cache.CachedSession(backend="memory")

    def _init_version(self) -> None:
        if self.version:
            return
        return super()._init_version()

    def _init_soup(self) -> None:
        response = self.session.get(
            self.uri, headers=self.headers, allow_redirects=True
        )
        response.raise_for_status()
        self._soup_page = BeautifulSoup(response.content, features="html.parser")
        self._text_page = response.text

    def _init_download_link(self) -> None:
        self.download_link = self._determine_download_link()

    def _determine_download_link(self) -> str:
        for link in self._urls_with_download_regex():
            if (
                re.search(rf"{self._download_regex}$", link)
                and str(self.version) in link
            ):
                return link

        raise DownloadLinkNotFoundError(
            f"Download link not found for regex '{self._download_regex}' and version '{self.version}' on page '{self.uri}'"
        )

    def _determine_public_key(self) -> bytes:
        for url in self._urls():
            if any(url.endswith(ext) for ext in self.PUBKEY_EXTENSIONS):
                r = self.session.get(url)
                r.raise_for_status()
                return r.content
        raise RuntimeError("Could not find a public key")

    def _determine_signature(self) -> bytes:
        candidates: list[str] = []
        for url in self._urls():
            if any(url.endswith(ext) for ext in self.SIGNATURE_EXTENSIONS):
                candidates.append(url)

        if not candidates:
            raise RuntimeError("Could not find a signature")

        chosen_url: str = candidates[0]

        urls_with_dl_regex = self._urls_with_download_regex()
        for url in candidates:
            if url in urls_with_dl_regex:
                chosen_url = url
                if str(self.version) in url:
                    break

        r = self.session.get(chosen_url)
        r.raise_for_status()
        return r.content

    def _urls(self) -> list[str]:
        """
        (Protected) Get all URLs from the page.

        Returns:
            list[str]: A list of URLs found on the page.
        """
        results: list[str] = []
        for a_tag in self._soup_page.find_all("a", href=True):
            href = a_tag.get("href")
            if href and str(href).startswith("http"):
                results.append(str(href))
            else:
                results.append(urljoin(self.uri, str(href)))
        return results

    def _urls_with_download_regex(self) -> list[str]:
        """
        (Protected) Get all URLs from the page that match the regex.

        Returns:
            list[str]: A list of URLs matching the regex.
        """
        return [url for url in self._urls() if re.search(self._download_regex, url)]

    def _urls_with_version(self) -> list[str]:
        """
        (Protected) Get all URLs from the page that contain the version.

        Returns:
            list[str]: A list of URLs containing the version.
        """
        return [url for url in self._urls() if str(self.version) in url]

    def _determine_latest_version_from_search(self, regex, string) -> Version | None:
        version_match = re.search(regex, string)
        if (
            not version_match
            or not version_match.lastindex
            or version_match.lastindex < 1
        ):
            return None

        return self.VersionClass(
            version_match.group(1), self.version_separator, self.version_padding
        )

    def _determine_latest_version(self) -> Version:
        """
        (Protected) Determine the version from the page using the provided regex.

        Returns:
            str: The determined version.

        Raises:
            ValueError: If no version is found on the page.
        """
        latest_version = self.VersionClass("0")
        for url in self._urls_with_download_regex():
            logging.debug(
                f"Checking URL for version: {url} with regex {self._version_regex}"
            )
            current_version = self._determine_latest_version_from_search(
                self._version_regex, url
            )
            if current_version and current_version > latest_version:
                latest_version = current_version
        if latest_version == self.VersionClass("0"):
            current_version = self._determine_latest_version_from_search(
                self._version_regex, self._text_page
            )
            if current_version and current_version > latest_version:
                latest_version = current_version
        if latest_version == self.VersionClass("0"):
            raise ValueError(
                f"No version found on the page '{self.uri}' using regex '{self._version_regex}'"
            )
        return latest_version

    def _fetch_and_parse_sum(self, url: str) -> tuple[str, int]:
        sum_file = self.session.get(url, headers=self.headers)
        sum_file.raise_for_status()

        sum_file_text = sum_file.text.strip()
        if not re.search(self._download_regex, sum_file_text):
            if not re.search(r"\s", sum_file_text) and len(sum_file_text) > 0:
                return sum_file_text, 0
            raise ValueError(
                f"Download regex '{self._download_regex}' did not match in sum file text: '{sum_file_text}'"
            )

        sum_pos: int = 1 if re.search(rf"^{self._download_regex}", sum_file_text) else 0

        min_sum_file_text = ""
        for line in sum_file_text.splitlines():
            filename = line.split()[(sum_pos + 1) % 2]
            if str(self.version) in filename:
                min_sum_file_text += f"{line}\n"

        return min_sum_file_text or sum_file_text, sum_pos

    def _determine_sums(self) -> list[Checksum]:
        sums: list[Checksum] = []
        errors: list[str] = []
        for check in ["version", "file", "any"]:
            urls = self._urls() if check == "any" else self._urls_with_download_regex()
            for url in urls:
                if check == "version" and str(self.version) not in url:
                    continue

                for sum_type in SumType:
                    if not sum_type.matches(url):
                        continue

                    try:
                        sum_file_text, sum_pos = self._fetch_and_parse_sum(url)
                    except Exception as e:
                        errors.append(
                            f"Error fetching or parsing sum file from '{url}': {e}"
                        )
                        continue

                    has_whitespace = re.search(r"\s", sum_file_text)
                    hash_value = (
                        sum_file_text
                        if not has_whitespace
                        else parse_hash(sum_file_text, self._download_regex, sum_pos)
                    )
                    sums.append(Checksum.from_sum_type(sum_type, hash_value))
            if sums:
                return sums

        raise ValueError(
            f"Could not determine the sum type from the page at '{self.uri}'."
            + (f" Errors: {', '.join(errors)}" if errors else "")
        )

    def _determine_speed(self) -> float:
        PROBE_BYTES: int = 2048
        with requests.get(
            self.download_link, stream=True, timeout=10, headers=self.headers
        ) as response:
            response.raise_for_status()
            start = time.time_ns()
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                total_size += len(chunk)
                if total_size >= PROBE_BYTES:
                    break
            end = time.time_ns()

        elapsed_time = end - start
        if elapsed_time == 0:
            return float("inf")
        return total_size / elapsed_time

    def _download_file(self, file: Path) -> None:
        download_file(self.download_link, file)
