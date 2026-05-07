from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.OPNsense.OPNsense import OPNsense


class OPNsenseMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str, edition: str) -> None:
        mirrors: list[GenericMirror] = [OPNsense(arch, edition)]
        super().__init__(mirrors)
