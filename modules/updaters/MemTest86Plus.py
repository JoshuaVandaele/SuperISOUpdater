from pathlib import Path

from modules.mirrors.MemTest86Plus.MemTest86PlusMirrorManager import (
    MemTest86PlusMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class MemTest86Plus(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str, arch: str) -> None:
        self.valid_archs = ["x86_64", "i586"]
        self.arch = arch
        mirror_mgr = MemTest86PlusMirrorManager(arch)
        super().__init__(folder_path / file_name, mirror_mgr)
