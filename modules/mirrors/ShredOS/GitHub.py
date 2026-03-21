import re

from modules.Checksum import Checksum, SumType
from modules.GitHubVersion import GitHubVersion
from modules.mirrors.GitHubMirror import GitHubMirror


class GitHub(GitHubMirror):
    def __init__(self, arch: str) -> None:
        is_lite = arch == "i686"
        super().__init__(
            repository="PartialVolume/shredos.x86_64",
            file_regex=rf"shredos-.+{arch}.+\d+{'_lite' if is_lite else ''}\.iso",
            determine_version_using=GitHubVersion.TAG,
            has_signature=False,
            version_regex=r"v[\d\.]+_([\d\.]+)_",
        )
