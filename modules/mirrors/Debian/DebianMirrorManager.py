from modules.mirrors.Debian.Debian import Debian
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class DebianMirrorManager(GenericMirrorManager):
    def __init__(self, arch) -> None:
        mirrors: list[GenericMirror] = [Debian(arch)]
        super().__init__(mirrors)
