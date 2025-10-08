"""
Ventoy Updater

Ventoy is a tool to create bootable USB drives - it makes sense to keep it updated!
Downloads from GitHub Releases.
"""
from pathlib import Path
from modules.updaters.base.GitHubReleaseUpdater import GitHubReleaseUpdater

FILE_NAME = "ventoy-[[VER]]-linux.tar.gz"


class Ventoy(GitHubReleaseUpdater):
    """
    Updater for Ventoy bootable USB solution.
    
    Ventoy releases include Windows and Linux versions.
    We'll download the Linux tar.gz which is more universal.
    """
    
    github_repo = "ventoy/Ventoy"
    asset_pattern = r"ventoy-.*-linux\.tar\.gz$"
    
    def __init__(self, folder_path: Path) -> None:
        self.file_path = folder_path / FILE_NAME
        super().__init__(folder_path)
