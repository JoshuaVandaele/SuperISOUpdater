from pathlib import Path

from modules.mirrors.Proxmox.ProxmoxMirrorManager import ProxmoxMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Proxmox(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str, edition: str) -> None:
        self.valid_editions = ["ve", "mail-gateway", "backup-server"]
        self.edition = edition
        mirror_mgr = ProxmoxMirrorManager(edition)
        super().__init__(folder_path / file_name, mirror_mgr)
