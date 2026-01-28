from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.ShredOS.GitHub import GitHub


class ShredOSMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str, arch: str) -> None:
        mirrors: list[GenericMirror] = [GitHub(edition, arch)]
        super().__init__(mirrors)
