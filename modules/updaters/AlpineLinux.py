from pathlib import Path

from modules.mirrors.AlpineLinux.AlpineLinuxMirrorManager import (
    AlpineLinuxMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class AlpineLinux(GenericUpdater):
    def __init__(
        self, folder_path: Path, arch: str, edition: str, file_name: str
    ) -> None:
        self.valid_archs = [
            "aarch64",
            "armv7",
            "loongarch64",
            "ppc64le",
            "riscv64",
            "s390x",
            "x86",
            "x86_64",
        ]
        self.arch = arch
        self.valid_editions = ["standard"]
        self.edition = edition
        mirror_mgr = AlpineLinuxMirrorManager(arch, edition)
        super().__init__(folder_path / file_name, mirror_mgr)
