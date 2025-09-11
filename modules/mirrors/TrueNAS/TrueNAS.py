from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType


class TrueNAS(GenericMirror):
    def __init__(self) -> None:
        super().__init__(
            url="https://www.truenas.com/download-truenas-community-edition",
            file_regex=r"TrueNAS-SCALE-.+\.iso",
            version_regex=r"TrueNAS-SCALE-([\d\.]+)\.iso",
        )
