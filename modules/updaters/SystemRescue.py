from pathlib import Path

from modules.mirrors.SystemRescue.SystemRescueMirrorManager import (
    SystemRescueMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class SystemRescue(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str, arch: str) -> None:
        self.valid_archs = [
            "amd64",
        ]
        self.arch = arch
        mirror_mgr = SystemRescueMirrorManager(arch)
        super().__init__(folder_path / file_name, mirror_mgr)
