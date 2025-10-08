"""
EndeavourOS Updater

EndeavourOS is a user-friendly Arch-based Linux distribution.
Downloads from GitHub Releases.
"""
from pathlib import Path
import re
from functools import cache
from modules.updaters.base.GitHubReleaseUpdater import GitHubReleaseUpdater
from modules.exceptions import VersionNotFoundError

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
    
    @cache
    def _get_latest_version(self) -> list[str]:
        """Extract version from ISO filename instead of tag."""
        assets = self.release_data.get('assets', [])
        
        for asset in assets:
            if re.search(self.asset_pattern, asset['name'], re.IGNORECASE):
                # Extract date version from filename like EndeavourOS_Artemis_neo-2024.01.25.iso
                match = re.search(r'-([\d.]+)\.iso$', asset['name'])
                if match:
                    version_str = match.group(1)
                    # Convert dots and dashes to dots for version comparison
                    version_str = version_str.replace('-', '.')
                    return self._str_to_version(version_str)
        
        raise VersionNotFoundError(
            f"Could not extract version from asset names in release"
        )
    
    def check_integrity(self) -> bool:
        """EndeavourOS provides SHA512 checksums."""
        # TODO: Implement SHA512 verification from GitHub release assets
        return True
