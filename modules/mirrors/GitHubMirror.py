import re

import requests_cache

from modules.GitHubVersion import GitHubVersion
from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType
from modules.utils import parse_hash
from modules.Version import Version


class GitHubMirror(GenericMirror):
    API_URL = "https://api.github.com"

    def __init__(
        self,
        repository: str,
        file_regex: str,
        version_regex: str,
        version_padding: int = 0,
        determine_version_using: GitHubVersion = GitHubVersion.TAG,
    ) -> None:
        """Initialize the GitHubMirror.

        Args:
            repository (str): Repository name in the format 'owner/repo'.
            determine_version_using (GitHubVersion, optional): _description_. Defaults to GitHubVersion.TAG.
        """
        super().__init__(
            url=f"{self.API_URL}/repos/{repository}/releases",
            file_regex=file_regex,
            version_regex=version_regex,
            version_padding=version_padding,
        )
        self.determine_version_using = determine_version_using

    def initialize(self) -> None:
        github_data = self.session.get(self.url)
        github_data.raise_for_status()
        self.github_info = github_data.json()

        self.version: Version = (
            self._determine_version(self._version_regex)
            if self._version_regex
            else self._version
        )  # type: ignore

        types, sums = self._determine_sums()
        self.sum_types: list[SumType] = types
        self.sums: list[str] = sums
        self.download_link: str = self._get_download_link()
        self.speed: float = self._determine_speed()

    def _determine_version(self, version_regex: str) -> Version:
        latest_version = Version("0")
        self.current_release_json = {}
        for release in self.github_info:
            if (
                self.determine_version_using == GitHubVersion.TAG
                or self.determine_version_using == GitHubVersion.NAME
            ):
                if self.determine_version_using == GitHubVersion.TAG:
                    version_key = "tag_name"
                else:
                    version_key = "name"
                current_version = self._determine_version_from_search(
                    version_regex, release[version_key]
                )
                if current_version and current_version > latest_version:
                    latest_version = current_version
                    self.current_release_json = release
            elif self.determine_version_using == GitHubVersion.FILE_NAME:
                for asset in release["assets"]:
                    current_version = self._determine_version_from_search(
                        version_regex, asset["name"]
                    )
                    if current_version and current_version > latest_version:
                        latest_version = current_version
                        self.current_release_json = release
        if latest_version == Version("0"):
            raise ValueError(
                f"No version found on the page '{self._url}' using regex '{version_regex}'"
            )
        return latest_version

    def _urls(self) -> list[str]:
        files = []
        for release in self.github_info:
            for asset in release["assets"]:
                files.append(asset["browser_download_url"])
        return files

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        def fetch_and_parse_sum() -> tuple[str, int]:
            sum_file = self.session.get(url)
            sum_file.raise_for_status()

            sum_file_text = sum_file.text.strip()
            if not re.search(self._file_regex, sum_file_text):
                raise ValueError(
                    f"File regex '{self._file_regex}' did not match in sum file text:\n'{sum_file_text}'"
                )

            sum_pos: int = 1 if re.search(rf"^{self._file_regex}", sum_file_text) else 0
            return sum_file_text, sum_pos

        sums: list[str] = []
        sum_types: list[SumType] = []
        errors: list[str] = []

        for asset in self.current_release_json.get("assets", []):
            url = asset["browser_download_url"]
            found_for_url: bool = False
            for sum_type, filenames in self.CHECKSUM_FILENAMES.items():
                if found_for_url:
                    break
                for filename in filenames:
                    if filename not in url:
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
                    found_for_url = True
                    break
            if found_for_url:
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
                break

        if not sums or not sum_types:
            raise ValueError(
                f"No sums found on the page '{self._url}' using file regex '{self._file_regex}'."
                + f" Errors: {', '.join(errors)}"
                if errors
                else "No sums found."
            )
        return sum_types, sums
