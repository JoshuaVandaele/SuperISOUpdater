from modules.GitHubVersion import GitHubVersion
from modules.mirrors.GitHubMirror import GitHubMirror
from modules.Version import Version


class GitHub(GitHubMirror):
    def __init__(self, edition: str) -> None:
        super().__init__(
            repository="rescuezilla/rescuezilla",
            file_regex=rf"rescuezilla-.+-64bit.{edition}.iso",
            determine_version_using=GitHubVersion.TAG,
            version_regex=r"(.+)",
        )

    def _determine_version(self, version_regex: str) -> Version:
        self.github_info = [
            release
            for release in self.github_info
            if "rolling" not in release["tag_name"]
        ]
        return super()._determine_version(version_regex)
