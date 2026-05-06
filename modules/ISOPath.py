import os


class ISOPath(str):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        if not self.has_version():
            raise ValueError("Invalid name. The name needs a [[VER]] tag.")

    def has_version(self) -> bool:
        return "[[VER]]" in self

    def has_edition(self) -> bool:
        return "[[EDITION]]" in self

    def has_lang(self) -> bool:
        return "[[LANG]]" in self

    def has_arch(self) -> bool:
        return "[[ARCH]]" in self

    def fill_placeholders(
        self,
        version: str | None = None,
        edition: str | None = None,
        lang: str | None = None,
        arch: str | None = None,
        extension: str | None = None,
    ) -> str:
        result = self
        if version and self.has_version():
            result = result.replace("[[VER]]", version)
        if edition and self.has_edition():
            result = result.replace("[[EDITION]]", edition)
        if lang and self.has_lang():
            result = result.replace("[[LANG]]", lang)
        if arch and self.has_arch():
            result = result.replace("[[ARCH]]", arch)
        if extension:
            result += f".{extension}"
        return result

    def basename(self) -> ISOPath:
        return ISOPath(os.path.basename(self))

    def dirname(self) -> str:
        return os.path.dirname(self)
