from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.MXLinux.Crihan import Crihan
from modules.mirrors.MXLinux.MXLinux import MXLinux


class MXLinuxMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str, edition: str) -> None:
        mirrors: list[GenericMirror] = [MXLinux(arch, edition), Crihan(arch, edition)]
        super().__init__(mirrors)
