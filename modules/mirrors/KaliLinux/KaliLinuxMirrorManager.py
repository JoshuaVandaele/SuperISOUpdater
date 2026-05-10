from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.KaliLinux.KaliLinuxHTTP import KaliLinuxHTTP
from modules.mirrors.KaliLinux.KaliLinuxTorrent import KaliLinuxTorrent


class KaliLinuxMirrorManager(GenericMirrorManager):
    def __init__(self, arch, edition) -> None:
        mirrors: list[GenericMirror] = [
            KaliLinuxTorrent(arch, edition),
            KaliLinuxHTTP(arch, edition),
        ]
        super().__init__(mirrors)
