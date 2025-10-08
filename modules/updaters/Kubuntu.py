"""
Kubuntu Updater

Kubuntu is the Ubuntu flavor with KDE Plasma desktop environment.
"""
from pathlib import Path
from modules.updaters.base.UbuntuVariantUpdater import UbuntuVariantUpdater

FILE_NAME = "kubuntu-[[VER]]-desktop-amd64.iso"


class Kubuntu(UbuntuVariantUpdater):
    """
    Updater for Kubuntu.
    
    Kubuntu is the Ubuntu variant with KDE Plasma desktop.
    """
    
    variant_name = "kubuntu"
    file_name_template = FILE_NAME
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
