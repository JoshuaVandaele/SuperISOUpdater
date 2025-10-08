from modules.mirrors.GenericComplexMirror import GenericComplexMirror
from modules.SumType import SumType
from modules.Version import Version
import re


class HirensBootCD(GenericComplexMirror):
    def __init__(self) -> None:
        super().__init__(
            url="https://www.hirensbootcd.org/download/",
            # Match (v1.0.0)
            version_regex=r"\(v((\d+\.?)+)\)",
        )

    def _determine_version(self, version_regex: str) -> Version:
        version_pattern = re.compile(version_regex)

        version = version_pattern.search(self._text_page)
        if version:
            return Version(version.group(1))
        return None

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        sha256_pattern = re.compile(r"\b[a-fA-F0-9]{64}\b")

        matches = sha256_pattern.findall(self._text_page)

        sum_types = [SumType.SHA256] * len(matches)

        return sum_types, matches

    def _get_download_link(self) -> str:
        return "https://www.hirensbootcd.org/files/HBCD_PE_x64.iso"
