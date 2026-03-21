from pathlib import Path

from modules.mirrors.ShredOS.ShredOSMirrorManager import ShredOSMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class ShredOS(GenericUpdater):
    def __init__(self, folder_path: Path, arch: str, file_name: str) -> None:
        self.valid_archs = ["x86-64", "i686"]
        self.arch = arch
        mirror_mgr = ShredOSMirrorManager(arch)
        super().__init__(folder_path / file_name, mirror_mgr)
