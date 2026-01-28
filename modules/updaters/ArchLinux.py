from pathlib import Path

from modules.mirrors.ArchLinux.ArchLinuxMirrorManager import ArchLinuxMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class ArchLinux(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str, arch: str) -> None:
        mirror_mgr = ArchLinuxMirrorManager(arch)
        super().__init__(folder_path / file_name, mirror_mgr)
