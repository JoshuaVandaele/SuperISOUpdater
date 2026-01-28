import re
from pathlib import Path

from bs4 import BeautifulSoup

from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType
from modules.Version import Version


class GenericComplexMirror(GenericMirror):

    def __init__(
        self,
        url: str,
        version_regex: str | None = None,
        version_separator: str = ".",
        version_padding: int = 0,
        version: Version | None = None,
        version_class=Version,
        has_signature: bool = True,
        signature_file: Path | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initializes the GenericMirror with a URL and a search regex.

        Args:
            url (str): The URL to find the version on.
            version_regex (str, optional): A regex pattern to search for the version on the page. If not provided, the version must be specified with the `version` parameter.
            version_separator (str, optional): The version separator for each component of a version. Used with `version_regex`. Defaults to "."
            version (Version, optional): The version of the file to download. If not provided, it will be determined from the page using `version_regex`.
            headers (dict[str, str], optional): Headers to pass along for all requests.
        """
        if not version_regex and not version:
            raise ValueError(
                "Either 'version_regex' or 'version' must be provided to determine the version."
            )
        super().__init__(
            url,
            "",  # file_regex goes unused #
            version_regex,
            version_separator,
            version_padding,
            version,
            version_class,
            has_signature,
            signature_file,
            headers,
        )

    def _determine_version(self, version_regex: str) -> Version:
        latest_version = self._VersionClass("0")

        matches = re.findall(version_regex, self._text_page)

        for match in matches:
            version_str = match[0] if isinstance(match, tuple) else match
            current_version = self._VersionClass(
                version_str,
                self._version_separator,
                self._version_padding,
            )
            if current_version and current_version > latest_version:
                latest_version = current_version

        if latest_version == self._VersionClass("0"):
            raise ValueError(
                f"No version found on the page '{self._url}' using regex '{version_regex}'"
            )
        return latest_version

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        raise NotImplementedError()

    def _get_download_link(self) -> str:
        raise NotImplementedError()
