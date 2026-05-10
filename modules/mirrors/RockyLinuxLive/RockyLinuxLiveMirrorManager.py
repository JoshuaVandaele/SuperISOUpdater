from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.RockyLinuxLive.OVH import OVH
from modules.mirrors.RockyLinuxLive.RockyLinux import RockyLinux


class RockyLinuxLiveMirrorManager(GenericMirrorManager):
    def __init__(self, arch, edition) -> None:
        mirrors: list[GenericMirror] = [RockyLinux(arch, edition), OVH(arch, edition)]
        super().__init__(mirrors)
