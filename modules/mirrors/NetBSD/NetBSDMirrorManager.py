from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.NetBSD.NetBSD import NetBSD
from modules.mirrors.NetBSD.NetBSDCDN import NetBSDCDN
from modules.mirrors.NetBSD.NetBSDFR import NetBSDFR


class NetBSDMirrorManager(GenericMirrorManager):
    def __init__(self, arch) -> None:
        mirrors: list[GenericMirror] = [NetBSD(arch), NetBSDCDN(arch), NetBSDFR(arch)]
        super().__init__(mirrors)
