from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror


class ClientVPS(GenericHTTPMirror):
    def __init__(self) -> None:
        super().__init__(
            uri="https://mirror.clientvps.com/ubcd/",
            download_regex=r"ubcd.+\.iso",
            version_regex=r"ubcd(\d+)\.iso",
            version_separator="",
            has_signature=False,
        )
