from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.MemTest86Plus.Memtest import Memtest


class MemTest86PlusMirrorManager(GenericMirrorManager):
    def __init__(
        self,
    ) -> None:
        mirrors: list[GenericMirror] = [Memtest()]
        super().__init__(mirrors)
