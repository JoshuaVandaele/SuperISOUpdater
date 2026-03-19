from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.LinuxMint.Kernel import Kernel


class LinuxMintMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str) -> None:
        mirrors: list[GenericMirror] = [Kernel(edition)]
        super().__init__(mirrors)
