from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Manjaro.Manjaro import Manjaro


class ManjaroMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str) -> None:
        mirrors: list[GenericMirror] = [Manjaro(edition)]
        super().__init__(mirrors)
