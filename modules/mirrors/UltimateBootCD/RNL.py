from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror


class RNL(GenericHTTPMirror):
    def __init__(self) -> None:
        super().__init__(
            uri="https://ftp.rnl.tecnico.ulisboa.pt/pub/UBCD/",
            download_regex=r"ubcd.+\.iso",
            version_regex=r"ubcd(\d+)\.iso",
            version_separator="",
            has_signature=False,
        )
