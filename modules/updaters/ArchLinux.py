from pathlib import Path

from modules.mirrors.ArchLinux.ArchLinuxMirrorManager import ArchLinuxMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class ArchLinux(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str) -> None:
        mirror_mgr = ArchLinuxMirrorManager()
        super().__init__(folder_path / file_name, mirror_mgr)
        if not self.has_version():
            raise ValueError("ArchLinux needs a [[VER]] tag.")
