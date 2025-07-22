from pathlib import Path

from modules.mirrors.UltimateBootCD.UltimateBootCDMirrorManager import (
    UltimateBootCDMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class UltimateBootCD(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str) -> None:
        mirror_mgr = UltimateBootCDMirrorManager()
        super().__init__(folder_path / file_name, mirror_mgr)
        if not self.has_version():
            raise ValueError("UltimateBootCD needs a [[VER]] tag.")
