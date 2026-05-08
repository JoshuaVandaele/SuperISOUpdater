from modules.mirrors.RockyLinux.OVH import OVH
from modules.mirrors.RockyLinux.RockyLinux import RockyLinux
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class RockyLinuxMirrorManager(GenericMirrorManager):
    def __init__(self, arch, edition) -> None:
        mirrors: list[GenericMirror] = [RockyLinux(arch, edition), OVH(arch, edition)]
        super().__init__(mirrors)
