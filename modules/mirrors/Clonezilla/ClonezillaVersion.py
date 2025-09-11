import re

from modules.ParsedTokens import ParsedTokens
from modules.Version import Version


class ClonezillaVersion(Version):
    def __init__(self, version_string: str, separator=".", zero_pad=0) -> None:
        """
        Initializes a Version object with major, minor, and patch components.

        Args:
            version_string (str):
            zero_pad (int): The number of digits to zero-pad each component. Defaults to 0.
        """
        if not version_string:
            raise ValueError("The version string cannot be empty.")
        self.zero_pad = zero_pad
        components: list[str] = re.split(r"[.-]", version_string)
        self._parsed_components: list[ParsedTokens] = [
            self._parse_component(c) for c in components
        ]

    def __str__(self) -> str:
        str_components = [
            "".join(
                (
                    f"{tok:0{self.zero_pad}d}"
                    if isinstance(tok, int) and self.zero_pad > 0
                    else str(tok)
                )
                for tok in comp
            )
            for comp in self._parsed_components
        ]
        if len(str_components) <= 1:
            return str_components[0]

        return ".".join(str_components[:-1]) + "-" + str_components[-1]

    def __repr__(self) -> str:
        return str(self)
