from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.LinuxMint.Kernel import Kernel
from modules.mirrors.LinuxMint.LinuxMint import LinuxMint


class LinuxMintMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str) -> None:
        mirrors: list[GenericMirror] = [LinuxMint(edition), Kernel(edition)]
        super().__init__(mirrors)
