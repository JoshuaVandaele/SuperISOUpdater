from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.ShredOS.GitHub import GitHub


class ShredOSMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str) -> None:
        mirrors: list[GenericMirror] = [GitHub(arch)]
        super().__init__(mirrors)
