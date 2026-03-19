from pathlib import Path

from modules.mirrors.Ubuntu.UbuntuMirrorManager import UbuntuMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Ubuntu(GenericUpdater):
    def __init__(
        self, folder_path: Path, file_name: str, arch: str, edition: str
    ) -> None:
        self.valid_archs = [
            "amd64",
        ]
        self.arch = arch
        self.valid_editions = ["desktop", "live-server"]
        self.edition = edition
        mirror_mgr = UbuntuMirrorManager(arch, edition)
        super().__init__(folder_path / file_name, mirror_mgr)
