from modules.mirrors.CachyOS.ATCachyOS import ATCachyOS
from modules.mirrors.CachyOS.USCachyOS import USCachyOS
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class CachyOSMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str) -> None:
        mirrors: list[GenericMirror] = [USCachyOS(edition), ATCachyOS(edition)]
        super().__init__(mirrors)
