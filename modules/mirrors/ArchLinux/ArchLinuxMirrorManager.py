from modules.mirrors.ArchLinux.GeoMirror import GeoMirror
from modules.mirrors.ArchLinux.Infania import Infania
from modules.mirrors.ArchLinux.Rackspace import Rackspace
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class ArchLinuxMirrorManager(GenericMirrorManager):
    def __init__(self, arch) -> None:
        mirrors = [GeoMirror(arch), Infania(arch), Rackspace(arch)]
        super().__init__(mirrors)
