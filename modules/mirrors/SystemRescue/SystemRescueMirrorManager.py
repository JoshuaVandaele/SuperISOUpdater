from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.SystemRescue.Fastly import Fastly


class SystemRescueMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str) -> None:
        mirrors: list[GenericMirror] = [Fastly(arch)]
        super().__init__(mirrors)
