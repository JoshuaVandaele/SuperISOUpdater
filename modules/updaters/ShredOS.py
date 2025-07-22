from pathlib import Path

from modules.mirrors.ShredOS.ShredOSMirrorManager import ShredOSMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class ShredOS(GenericUpdater):
    def __init__(self, folder_path: Path, edition: str, file_name: str) -> None:
        self.valid_editions = ["vanilla", "nomodeset"]
        self.edition = edition.lower()
        mirror_mgr = ShredOSMirrorManager(edition)
        super().__init__(folder_path / file_name, mirror_mgr)
