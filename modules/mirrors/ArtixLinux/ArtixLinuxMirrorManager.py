from modules.mirrors.ArtixLinux.Akardam import Akardam
from modules.mirrors.ArtixLinux.ArkHost import ArkHost
from modules.mirrors.ArtixLinux.ArtixLinux import ArtixLinux
from modules.mirrors.ArtixLinux.DotSrc import DotSrc
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class ArtixLinuxMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str, arch: str) -> None:
        mirrors = [
            Akardam(edition, arch),
            ArkHost(edition, arch),
            ArtixLinux(edition, arch),
            DotSrc(edition, arch),
        ]
        super().__init__(mirrors)
