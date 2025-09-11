import re

from modules.ParsedTokens import ParsedTokens, Token


class Version:
    _token_regex = re.compile(r"\d+|[A-Za-z]+")

    def __init__(
        self, version_string: str, separator: str = ".", zero_pad: int = 0
    ) -> None:
        """
        Initializes a Version object with major, minor, and patch components.

        Args:
            version_string (str):
            separator (str): The separator used to join the components. Defaults to '.'.
            zero_pad (int): The number of digits to zero-pad each component. Defaults to 0.
        """
        if not version_string:
            raise ValueError("The version string cannot be empty.")
        self.separator = separator
        self.zero_pad = zero_pad
        self.components: list[str] = (
            version_string.split(self.separator)
            if self.separator
            else list(version_string)
        )
        self._parsed_components: list[ParsedTokens] = [
            self._parse_component(c) for c in self.components
        ]

    @staticmethod
    def _parse_component(component: str) -> ParsedTokens:
        tokens = ParsedTokens()
        for token in Version._token_regex.findall(component):
            if token.isdigit():
                tokens.append(int(token))
            else:
                tokens.append(token)
        return tokens

    @staticmethod
    def _cmp_tokens(left: Token, right: Token) -> int:
        a = left
        b = right
        if isinstance(a, int) and isinstance(b, int):
            return (a > b) - (a < b)

        if isinstance(a, int):
            return -1
        if isinstance(b, int):
            return 1

        return (a > b) - (a < b)

    @classmethod
    def _compare_parsed(
        cls, left_tokens: ParsedTokens, right_tokens: ParsedTokens
    ) -> int:
        for left_token, right_token in zip(left_tokens, right_tokens):
            c = cls._cmp_tokens(left_token, right_token)
            if c:
                return c

        return (len(left_tokens) > len(right_tokens)) - (
            len(left_tokens) < len(right_tokens)
        )

    def _compare(self, other: "Version") -> int:
        for me, you in zip(self._parsed_components, other._parsed_components):
            c = self._compare_parsed(me, you)
            if c:
                return c

        return (len(self._parsed_components) > len(other._parsed_components)) - (
            len(self._parsed_components) < len(other._parsed_components)
        )

    def __str__(self) -> str:
        return self.separator.join(
            "".join(
                (
                    f"{tok:0{self.zero_pad}d}"
                    if isinstance(tok, int) and self.zero_pad > 0
                    else str(tok)
                )
                for tok in comp
            )
            for comp in self.components
        )

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._compare(other) == 0
        raise NotImplementedError

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._compare(other) < 0
        raise NotImplementedError

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._compare(other) > 0
        raise NotImplementedError

    def __le__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._compare(other) <= 0
        raise NotImplementedError

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._compare(other) >= 0
        raise NotImplementedError
