from modules.mirrors.ArchLinux.GeoMirror import GeoMirror
from modules.mirrors.ArchLinux.Infania import Infania
from modules.mirrors.ArchLinux.Rackspace import Rackspace
from modules.mirrors.GenericMirrorManager import GenericMirrorManager


class ArchLinuxMirrorManager(GenericMirrorManager):
    def __init__(
        self,
    ) -> None:
        mirrors = [GeoMirror(), Infania(), Rackspace()]
        super().__init__(mirrors)
