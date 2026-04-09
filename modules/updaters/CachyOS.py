from pathlib import Path

from modules.mirrors.CachyOS.CachyOSMirrorManager import CachyOSMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class CachyOS(GenericUpdater):
    def __init__(self, folder_path: Path, edition: str, file_name: str) -> None:
        self.valid_editions = ["desktop", "handheld"]
        self.edition = edition
        mirror_mgr = CachyOSMirrorManager(edition)
        super().__init__(folder_path / file_name, mirror_mgr)
