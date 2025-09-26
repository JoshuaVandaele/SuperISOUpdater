from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Windows10.Microsoft import Microsoft


class Windows10MirrorManager(GenericMirrorManager):
    def __init__(self, lang) -> None:
        mirrors: list[GenericMirror] = [Microsoft(lang)]
        super().__init__(mirrors)
