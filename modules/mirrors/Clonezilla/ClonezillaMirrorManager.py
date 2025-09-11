from modules.mirrors.Clonezilla.SourceForge import SourceForge
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class ClonezillaMirrorManager(GenericMirrorManager):
    def __init__(
        self,
    ) -> None:
        mirrors: list[GenericMirror] = [SourceForge()]
        super().__init__(mirrors)
