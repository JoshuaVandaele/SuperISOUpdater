from pathlib import Path

from modules.mirrors.TrueNAS.TrueNASMirrorManager import TrueNASMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class TrueNAS(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str) -> None:
        mirror_mgr = TrueNASMirrorManager()
        super().__init__(folder_path / file_name, mirror_mgr)
