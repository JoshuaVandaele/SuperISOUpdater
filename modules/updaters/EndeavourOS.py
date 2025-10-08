"""
EndeavourOS Updater

EndeavourOS is a user-friendly Arch-based Linux distribution.
Downloads from GitHub Releases.
"""
from pathlib import Path
from modules.updaters.base.GitHubReleaseUpdater import GitHubReleaseUpdater

FILE_NAME = "endeavouros-[[VER]].iso"


class EndeavourOS(GitHubReleaseUpdater):
    """
    Updater for EndeavourOS.
    
    EndeavourOS releases ISOs through GitHub Releases.
    """
    
    github_repo = "endeavouros-team/ISO"
    asset_pattern = r"EndeavourOS_[^-]+-[\d-]+\.iso$"
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
    
    def check_integrity(self) -> bool:
        """EndeavourOS provides SHA512 checksums."""
        # TODO: Implement SHA512 verification from GitHub release assets
        return True
