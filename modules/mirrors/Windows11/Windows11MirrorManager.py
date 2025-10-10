from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Windows11.Microsoft import Microsoft


class Windows11MirrorManager(GenericMirrorManager):
    def __init__(self, lang, arch) -> None:
        mirrors: list[GenericMirror] = [Microsoft(lang, arch)]
        super().__init__(mirrors)
