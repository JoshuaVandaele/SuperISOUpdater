from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Ubuntu.OVH import OVH


class UbuntuMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str, edition: str) -> None:
        mirrors: list[GenericMirror] = [OVH(arch, edition)]
        super().__init__(mirrors)
