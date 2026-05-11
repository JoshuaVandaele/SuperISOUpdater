from modules.mirrors.EndeavourOS.Gigenet import Gigenet
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class EndeavourOSMirrorManager(GenericMirrorManager):
    def __init__(self) -> None:
        mirrors: list[GenericMirror] = [Gigenet()]
        super().__init__(mirrors)
