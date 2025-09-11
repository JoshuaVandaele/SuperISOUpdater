from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.TrueNAS.TrueNAS import TrueNAS


class TrueNASMirrorManager(GenericMirrorManager):
    def __init__(
        self,
    ) -> None:
        mirrors: list[GenericMirror] = [TrueNAS()]
        super().__init__(mirrors)
