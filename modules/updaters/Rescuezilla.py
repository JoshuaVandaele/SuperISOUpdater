from pathlib import Path

from modules.mirrors.Rescuezilla.RescuezillaMirrorManager import (
    RescuezillaMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class Rescuezilla(GenericUpdater):
    def __init__(self, folder_path: Path, edition: str, file_name: str) -> None:
        self.valid_editions = ["bionic", "focal", "jammy", "noble"]
        self.edition = edition.lower()
        mirror_mgr = RescuezillaMirrorManager(edition)
        super().__init__(folder_path / file_name, mirror_mgr)
