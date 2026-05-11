from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Xubuntu.Free import Free
from modules.mirrors.Xubuntu.Ubuntu import Ubuntu


class XubuntuMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str, edition: str) -> None:
        mirrors: list[GenericMirror] = [Free(arch, edition), Ubuntu(arch, edition)]
        super().__init__(mirrors)
