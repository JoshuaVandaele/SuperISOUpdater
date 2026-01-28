from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.HirensBootCDPE.HirensBootCD import HirensBootCD


class HirensBootCDPEMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str) -> None:
        mirrors: list[GenericMirror] = [HirensBootCD(arch)]
        super().__init__(mirrors)
