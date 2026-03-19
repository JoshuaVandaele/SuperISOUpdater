from pathlib import Path

from modules.mirrors.LinuxMint.LinuxMintMirrorManager import LinuxMintMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class LinuxMint(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str, edition: str) -> None:
        self.valid_editions = ["cinnamon", "mate", "xfce"]
        self.edition = edition
        mirror_mgr = LinuxMintMirrorManager(edition)
        super().__init__(folder_path / file_name, mirror_mgr)
