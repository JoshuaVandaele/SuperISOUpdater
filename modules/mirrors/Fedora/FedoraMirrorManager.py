from modules.mirrors.Fedora.Fedora import Fedora
from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class FedoraMirrorManager(GenericMirrorManager):
    def __init__(self, arch, edition, spin: bool) -> None:
        mirrors: list[GenericMirror] = [Fedora(arch, edition, spin)]
        super().__init__(mirrors)
