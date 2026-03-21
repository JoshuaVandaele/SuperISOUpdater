import re
from copy import deepcopy

from modules.Checksum import Checksum, MD5Sum
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.Version import Version


class HDAT2(GenericHTTPMirror):
    def __init__(self, edition: str, ext: str) -> None:
        self.lite = edition == "lite"
        self.ext = ext

        extra = ""
        if self.lite:
            extra = "_lite"
        elif edition == "diskette":
            extra = "g"

        super().__init__(
            uri=f"https://www.hdat2.com/download.html",
            file_regex=rf"hdat2..{extra}_(\d+).{ext}",
            version_regex=rf"hdat2..{extra}_(\d+).{ext}",
            version_separator="",
            has_signature=False,
        )

    def _determine_sums(self) -> list[Checksum]:
        normal_version: Version = deepcopy(self.version)  # type: ignore
        normal_version.separator = "."
        search_r = f">{"Lite " if self.lite else ""}{self.ext.upper()} {normal_version} MD5=(.+)<"
        sum_match = re.search(search_r, self._text_page)
        if not sum_match:
            raise ValueError(f"Sum regex '{search_r}' could not be found on {self.uri}")
        return [MD5Sum(sum_match.group(1))]
