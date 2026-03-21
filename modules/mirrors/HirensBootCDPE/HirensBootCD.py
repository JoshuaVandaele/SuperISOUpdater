import logging
import re

from modules.Checksum import Checksum, SHA256Sum
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.Version import Version


class HirensBootCD(GenericHTTPMirror):
    def __init__(self, arch: str) -> None:
        self.arch = arch
        super().__init__(
            uri="https://www.hirensbootcd.org/download/",
            file_regex=rf"HBCD_PE_{self.arch}.iso",
            version_regex=r"\(v([\d\.]+)\)",
            has_signature=False,
        )

    def _determine_download_link(self) -> str:
        return f"https://www.hirensbootcd.org/files/HBCD_PE_{self.arch}.iso"

    def _determine_latest_version(self) -> Version:
        version_pattern = re.compile(self._version_regex)
        version = version_pattern.search(self._text_page)
        if version:
            return Version(version.group(1))
        raise ValueError(
            f"No version found on the page '{self.uri}' using regex '{self._version_regex}'"
        )

    def _determine_sums(self) -> list[Checksum]:
        # TODO: Extract all checksums
        sha256_pattern = re.compile(r"\b[a-fA-F0-9]{64}\b")
        matches = sha256_pattern.findall(self._text_page)
        return [SHA256Sum(match) for match in matches]
