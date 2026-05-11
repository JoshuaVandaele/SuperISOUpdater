from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Kubuntu.MirrorService import MirrorService
from modules.mirrors.Kubuntu.Ubuntu import Ubuntu


class KubuntuMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str, edition: str) -> None:
        mirrors: list[GenericMirror] = [
            MirrorService(arch, edition),
            Ubuntu(arch, edition),
        ]
        super().__init__(mirrors)
