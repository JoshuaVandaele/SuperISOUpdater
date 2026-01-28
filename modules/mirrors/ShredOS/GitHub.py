import re

from modules.GitHubVersion import GitHubVersion
from modules.mirrors.GitHubMirror import GitHubMirror
from modules.SumType import SumType


class GitHub(GitHubMirror):
    def __init__(self, edition: str, arch) -> None:
        super().__init__(
            repository="PartialVolume/shredos.x86_64",
            file_regex=rf"shredos-.+{arch}.+{edition}\.iso",
            determine_version_using=GitHubVersion.NAME,
            has_signature=False,
            version_regex=rf"v.+?_(.+?)_.+",
        )

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        for release in self.github_info:
            if str(self.version) in release["name"]:
                body: str = release["body"]
                line: str = next(
                    line.strip()
                    for line in body.splitlines()
                    if ("sha" in line or "md5" in line)
                    and re.search(self._file_regex, line)
                )
                sums = line.split(" ")
                sum_type = SumType(sums[0])
                sum_value: str = sums[1]
                return [sum_type], [sum_value]
        raise ValueError(f"Could not determine the sum type.")
