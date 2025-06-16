Token = int | str


class ParsedTokens(list):
    def __init__(self, tokens: list[Token] | None = None):
        super().__init__(tokens or [])

    def __str__(self) -> str:
        return "".join(map(str, self))
