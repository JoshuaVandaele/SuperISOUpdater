from modules.mirrors.GenericMirror import GenericMirror
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.Proxmox.Proxmox import Proxmox


class ProxmoxMirrorManager(GenericMirrorManager):
    def __init__(self, edition: str) -> None:
        mirrors: list[GenericMirror] = [Proxmox(edition)]
        super().__init__(mirrors)
