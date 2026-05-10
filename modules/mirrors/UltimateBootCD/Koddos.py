from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror


class Koddos(GenericHTTPMirror):
    def __init__(self) -> None:
        super().__init__(
            uri="http://mirror.koddos.net/ubcd/",
            download_regex=r"ubcd.+\.iso",
            version_regex=r"ubcd(\d+)\.iso",
            version_separator="",
            has_signature=False,
        )
