import requests

from modules.GitHubVersion import GitHubVersion
from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType
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
        super().__init__(
            url=f"{self.API_URL}/repos/{repository}/releases",
            file_regex=file_regex,
            version_regex=version_regex,
            version_padding=version_padding,
        )
        self.determine_version_using = determine_version_using

    def initialize(self) -> None:
        github_data = requests.get(self.url)
        github_data.raise_for_status()
        self.github_info = github_data.json()

        self.version: Version = (
            self._determine_version(self._version_regex)
            if self._version_regex
            else self._version
        )  # type: ignore

        types, sums = self._determine_sums()
        print(f"Found {len(types)} sum types and {len(sums)} sums")
        self.sum_types: list[SumType] = types
        self.sums: list[str] = sums
        self.download_link: str = self._get_download_link()
        self.speed: float = self._determine_speed()

    def _determine_version(self, version_regex: str) -> Version:
        latest_version = Version("0")
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
            elif self.determine_version_using == GitHubVersion.FILE_NAME:
                for asset in release["assets"]:
                    current_version = self._determine_version_from_search(
                        version_regex, asset["name"]
                    )
                    if current_version and current_version > latest_version:
                        latest_version = current_version
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
