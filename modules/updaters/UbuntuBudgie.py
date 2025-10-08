"""
Ubuntu Budgie Updater

Ubuntu Budgie is the Ubuntu flavor with Budgie desktop environment.
"""
from pathlib import Path
from modules.updaters.base.UbuntuVariantUpdater import UbuntuVariantUpdater

FILE_NAME = "ubuntu-budgie-[[VER]]-desktop-amd64.iso"


class UbuntuBudgie(UbuntuVariantUpdater):
    """
    Updater for Ubuntu Budgie.
    
    Ubuntu Budgie is the Ubuntu variant with modern Budgie desktop.
    """
    
    variant_name = "ubuntu-budgie"
    file_name_template = FILE_NAME
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
