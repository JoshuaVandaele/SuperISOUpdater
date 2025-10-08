"""
Puppy Linux Updater

Puppy Linux is a lightweight, fast Linux distribution that runs entirely in RAM.
Multiple "puplets" (variants) available.
"""
from pathlib import Path
from modules.updaters.base.DirectMirrorUpdater import DirectMirrorUpdater

FILE_NAME = "puppylinux-[[VER]].iso"


class PuppyLinux(DirectMirrorUpdater):
    """
    Updater for Puppy Linux (BionicPup variant as default).
    
    Puppy Linux has multiple variants - this downloads BionicPup (Ubuntu-based).
    """
    
    mirrors = [
        "http://distro.ibiblio.org/puppylinux/puppy-bionic/bionicpup64/",
        "https://mirrors.dotsrc.org/puppylinux/puppy-bionic/bionicpup64/",
    ]
    
    iso_pattern = r"bionicpup64-[\d.]+-uefi\.iso$"
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
