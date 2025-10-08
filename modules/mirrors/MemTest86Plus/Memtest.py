from modules.mirrors.GenericMirror import GenericMirror


class Memtest(GenericMirror):
    def __init__(self) -> None:
        super().__init__(
            url="https://www.memtest.org/",
            file_regex=r"mt86plus_(\d+\.?)+_64.iso\.zip",
            version_regex=r"mt86plus_(.+)_64\.iso\.zip",
        )
