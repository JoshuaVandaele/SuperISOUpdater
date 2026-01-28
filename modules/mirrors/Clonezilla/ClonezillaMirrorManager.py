from modules.mirrors.Clonezilla.SourceForge import SourceForge
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class ClonezillaMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str) -> None:
        mirrors: list[GenericMirror] = [SourceForge(arch)]
        super().__init__(mirrors)
