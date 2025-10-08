"""
Xubuntu Updater

Xubuntu is the Ubuntu flavor with Xfce desktop environment.
"""
from pathlib import Path
from modules.updaters.base.UbuntuVariantUpdater import UbuntuVariantUpdater

FILE_NAME = "xubuntu-[[VER]]-desktop-amd64.iso"


class Xubuntu(UbuntuVariantUpdater):
    """
    Updater for Xubuntu.
    
    Xubuntu is the lightweight Ubuntu variant with Xfce.
    """
    
    variant_name = "xubuntu"
    file_name_template = FILE_NAME
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
