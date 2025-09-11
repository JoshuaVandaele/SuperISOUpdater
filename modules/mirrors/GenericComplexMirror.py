import re

from bs4 import BeautifulSoup

from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType
from modules.Version import Version


class GenericComplexMirror(GenericMirror):

    def __init__(
        self,
        url: str,
        file_regex: str,
        version_regex: str | None = None,
        version_separator: str = ".",
        version_padding: int = 0,
        version: Version | None = None,
        version_class=Version,
    ) -> None:
        """
        Initializes the GenericMirror with a URL and a search regex.

        Args:
            url (str): The URL to find the version on.
            file_regex (str): A regex pattern to search for the file to download. The regex MUST include the very start and end of the file name.
            version_regex (str, optional): A regex pattern to search for the version on the page. If not provided, the version must be specified with the `version` parameter.
            version_separator (str, optional): The version separator for each component of a version. Used with `version_regex`. Defaults to "."
            version (Version, optional): The version of the file to download. If not provided, it will be determined from the page using `version_regex`.
        """
        if not version_regex and not version:
            raise ValueError(
                "Either 'version_regex' or 'version' must be provided to determine the version."
            )
        super().__init__(
            url,
            file_regex,
            version_regex,
            version_separator,
            version_padding,
            version,
            version_class,
        )

    def pre_init(self) -> None:
        pass

    def mid_init(self) -> None:
        pass

    def initialize(self) -> None:
        self.pre_init()
        text, soup = self._fetch_page(self._url)
        self._soup_page: BeautifulSoup = soup
        self._text_page: str = text

        self.version: Version = (
            self._determine_version(self._version_regex)
            if self._version_regex
            else self._version
        )  # type: ignore

        self.mid_init()

        types, sums = self._determine_sums()
        self.sum_types: list[SumType] = types
        self.sums: list[str] = sums
        self.download_link: str = self._get_download_link()
        self.speed: float = self._determine_speed()

        self.post_init()

    def post_init(self) -> None:
        pass

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
