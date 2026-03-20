from pathlib import Path

from modules.mirrors.Manjaro.ManjaroMirrorManager import ManjaroMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Manjaro(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str, edition: str) -> None:
        self.valid_editions = ["kde", "xfce", "gnome", "cinnamon", "i3"]
        self.edition = edition
        mirror_mgr = ManjaroMirrorManager(edition)
        super().__init__(folder_path / file_name, mirror_mgr)
