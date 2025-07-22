from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.UltimateBootCD.ClientVPS import ClientVPS
from modules.mirrors.UltimateBootCD.Koddos import Koddos
from modules.mirrors.UltimateBootCD.RNL import RNL


class UltimateBootCDMirrorManager(GenericMirrorManager):
    def __init__(
        self,
    ) -> None:
        mirrors = [RNL(), Koddos(), ClientVPS()]
        super().__init__(mirrors)
