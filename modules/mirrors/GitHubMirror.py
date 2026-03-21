import re

from modules.Checksum import Checksum, SumType
from modules.GitHubVersion import GitHubVersion
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import parse_hash
from modules.Version import Version


class GitHubMirror(GenericHTTPMirror):
    API_URL = "https://api.github.com"
    _init_steps: list[str] = [
        "_init_github",
        "_init_version",
        "_init_download_link",
        "_init_checksums",
        "_init_signature",
        "_init_speed",
    ]

    def __init__(
        self,
        repository: str,
        file_regex: str,
        version_regex: str,
        version_padding: int = 0,
        has_signature=True,
        determine_version_using: GitHubVersion = GitHubVersion.TAG,
    ) -> None:
        """Initialize the GitHubMirror.

        Args:
            repository (str): Repository name in the format 'owner/repo'.
            determine_version_using (GitHubVersion, optional): _description_. Defaults to GitHubVersion.TAG.
        """
        super().__init__(
            uri=f"{self.API_URL}/repos/{repository}/releases",
            file_regex=file_regex,
            version_regex=version_regex,
            version_padding=version_padding,
            has_signature=has_signature,
        )
        self.determine_version_using = determine_version_using

    def _init_github(self) -> None:
        github_data = self.session.get(self.uri)
        github_data.raise_for_status()
        self.github_info = github_data.json()

    def _determine_latest_version(self) -> Version:
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
                current_version = self._determine_latest_version_from_search(
                    self._version_regex, release[version_key]
                )
                if current_version and current_version > latest_version:
                    latest_version = current_version
                    self.current_release_json = release
            elif self.determine_version_using == GitHubVersion.FILE_NAME:
                for asset in release["assets"]:
                    current_version = self._determine_latest_version_from_search(
                        self._version_regex, asset["name"]
                    )
                    if current_version and current_version > latest_version:
                        latest_version = current_version
                        self.current_release_json = release
        if latest_version == Version("0"):
            raise ValueError(
                f"No version found on the page '{self.uri}' using regex '{self._version_regex}'"
            )
        return latest_version

    def _urls(self) -> list[str]:
        files = []
        for release in self.github_info:
            for asset in release["assets"]:
                files.append(asset["browser_download_url"])
        return files

    # TODO: Can we get rid of this?
    def _determine_sums(self) -> list[Checksum]:
        sums: list[Checksum] = []
        errors: list[str] = []
        for asset in self.current_release_json.get("assets", []):
            url = asset["browser_download_url"]
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
                    else parse_hash(sum_file_text, self._file_regex, sum_pos)
                )
                sums.append(Checksum.from_sum_type(sum_type, hash_value))
        if sums:
            return sums

        raise ValueError(
            f"Could not determine the sum type from the page at '{self.uri}'."
            + (f" Errors: {', '.join(errors)}" if errors else "")
        )
