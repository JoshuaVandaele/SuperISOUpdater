"""
Ubuntu MATE Updater

Ubuntu MATE is the Ubuntu flavor with MATE desktop environment.
"""
from pathlib import Path
from modules.updaters.base.UbuntuVariantUpdater import UbuntuVariantUpdater

FILE_NAME = "ubuntu-mate-[[VER]]-desktop-amd64.iso"


class UbuntuMATE(UbuntuVariantUpdater):
    """
    Updater for Ubuntu MATE.
    
    Ubuntu MATE is the Ubuntu variant with traditional MATE desktop.
    """
    
    variant_name = "ubuntu-mate"
    file_name_template = FILE_NAME
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
