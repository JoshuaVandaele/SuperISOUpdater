from pathlib import Path

from modules.mirrors.HirensBootCDPE.HirensBootCDPEMirrorManager import (
    HirensBootCDPEMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class HirensBootCDPE(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str, arch: str) -> None:
        self.valid_archs = [
            "x64",
        ]
        self.arch = arch
        mirror_mgr = HirensBootCDPEMirrorManager(arch)
        super().__init__(folder_path / file_name, mirror_mgr)
