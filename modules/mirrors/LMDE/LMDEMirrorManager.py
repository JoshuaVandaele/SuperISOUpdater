from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.LMDE.Kernel import Kernel
from modules.mirrors.LMDE.LinuxMint import LinuxMint


class LMDEMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str) -> None:
        mirrors: list[GenericMirror] = [LinuxMint(edition), Kernel(edition)]
        super().__init__(mirrors)
