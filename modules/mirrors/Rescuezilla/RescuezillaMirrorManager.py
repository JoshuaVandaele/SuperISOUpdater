from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Rescuezilla.GitHub import GitHub


class RescuezillaMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str, arch) -> None:
        mirrors: list[GenericMirror] = [GitHub(edition, arch)]
        super().__init__(mirrors)
