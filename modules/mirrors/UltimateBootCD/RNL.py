from modules.mirrors.GenericMirror import GenericMirror


class RNL(GenericMirror):
    def __init__(self) -> None:
        super().__init__(
            url="https://ftp.rnl.tecnico.ulisboa.pt/pub/UBCD/",
            file_regex=r"ubcd.+\.iso",
            version_regex=r"ubcd(\d+)\.iso",
            version_separator="",
            has_signature=False,
        )
