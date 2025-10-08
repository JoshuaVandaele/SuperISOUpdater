"""
Lubuntu Updater

Lubuntu is the Ubuntu flavor with LXQt desktop environment (formerly LXDE).
"""
from pathlib import Path
from modules.updaters.base.UbuntuVariantUpdater import UbuntuVariantUpdater

FILE_NAME = "lubuntu-[[VER]]-desktop-amd64.iso"


class Lubuntu(UbuntuVariantUpdater):
    """
    Updater for Lubuntu.
    
    Lubuntu is the lightweight Ubuntu variant with LXQt desktop.
    """
    
    variant_name = "lubuntu"
    file_name_template = FILE_NAME
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
