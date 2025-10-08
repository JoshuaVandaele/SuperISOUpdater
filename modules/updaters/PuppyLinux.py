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
        "http://distro.ibiblio.org/puppylinux/puppy-bionic/",
        "https://mirrors.dotsrc.org/puppylinux/puppy-bionic/",
    ]
    
    iso_pattern = r"bionicpup64.*\.iso$"
    
    def __init__(self, folder_path: Path) -> None:
        self.file_path = folder_path / FILE_NAME
        super().__init__(folder_path)
