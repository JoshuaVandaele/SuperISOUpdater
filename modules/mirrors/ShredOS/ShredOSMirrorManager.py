from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.ShredOS.GitHub import GitHub


class ShredOSMirrorManager(GenericMirrorManager):
    def __init__(
        self,
    ) -> None:
        edition: str = "vanilla"  # TODO: Add support for nomodeset
        mirrors: list[GenericMirror] = [GitHub(edition)]
        super().__init__(mirrors)
