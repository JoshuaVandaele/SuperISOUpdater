from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Tails.Tails import Tails


class TailsMirrorManager(GenericMirrorManager):
    def __init__(self, arch: str) -> None:
        mirrors: list[GenericMirror] = [Tails(arch)]
        super().__init__(mirrors)
