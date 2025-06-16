from modules.mirrors.GenericMirror import GenericMirror


class Koddos(GenericMirror):
    """
    A class representing a mirror for Koddos' Ultimate Boot CD (UBCD).
    """

    def __init__(self) -> None:
        super().__init__(
            url="http://mirror.koddos.net/ubcd/",
            file_regex=r"ubcd.+\.iso",
            version_regex=r"ubcd(\d+)\.iso",
            version_separator="",
        )
