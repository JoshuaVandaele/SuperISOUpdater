from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.UbuntuFlavor.MirrorService import MirrorService
from modules.mirrors.UbuntuFlavor.Ubuntu import Ubuntu


class UbuntuFlavorMirrorManager(GenericMirrorManager):
    def __init__(self, flavor: str, arch: str, edition: str) -> None:
        mirrors: list[GenericMirror] = [
            MirrorService(flavor, arch, edition),
            Ubuntu(flavor, arch, edition),
        ]
        super().__init__(mirrors)
