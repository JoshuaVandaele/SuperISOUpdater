from modules.mirrors.GenericMirror import GenericMirror


class ClientVPS(GenericMirror):
    def __init__(self) -> None:
        super().__init__(
            url="https://mirror.clientvps.com/ubcd/",
            file_regex=r"ubcd.+\.iso",
            version_regex=r"ubcd(\d+)\.iso",
            version_separator="",
        )
