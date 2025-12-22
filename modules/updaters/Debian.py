from pathlib import Path

from modules.mirrors.Debian.DebianMirrorManager import DebianMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Debian(GenericUpdater):
    def __init__(self, folder_path: Path, arch: str, file_name: str) -> None:
        self.valid_archs = [
            "amd64",
            "arm64",
            "armhf",
            "ppc64el",
            "riscv64",
            "s390x",
        ]
        self.arch = arch
        mirror_mgr = DebianMirrorManager(arch)
        super().__init__(folder_path / file_name, mirror_mgr)
