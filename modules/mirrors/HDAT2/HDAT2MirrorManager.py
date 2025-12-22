from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.HDAT2.HDAT2 import HDAT2


class HDAT2MirrorManager(GenericMirrorManager):
    def __init__(self, edition: str, ext: str) -> None:
        mirrors: list[GenericMirror] = [HDAT2(edition, ext)]
        super().__init__(mirrors)
