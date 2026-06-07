from modules.mirrors.FreeBSD.FreeBSD import FreeBSD
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class FreeBSDMirrorManager(GenericMirrorManager):
    def __init__(self, arch, edition) -> None:
        mirrors: list[GenericMirror] = [FreeBSD(arch, edition)]
        super().__init__(mirrors)
