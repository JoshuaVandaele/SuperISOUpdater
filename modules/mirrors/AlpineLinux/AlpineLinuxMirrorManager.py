from modules.mirrors.AlpineLinux.AlpineLinux import AlpineLinux
from modules.mirrors.AlpineLinux.OVH import OVH
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class AlpineLinuxMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str, edition: str) -> None:
        mirrors: list[GenericMirror] = [AlpineLinux(arch, edition), OVH(arch, edition)]
        super().__init__(mirrors)
