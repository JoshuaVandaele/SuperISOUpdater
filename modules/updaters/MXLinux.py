"""
MX Linux Updater

MX Linux is a popular Debian-based distribution known for stability.
Downloads from SourceForge.
"""
from functools import cache
from pathlib import Path
import requests
import re
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater

SOURCEFORGE_API = "https://sourceforge.net/projects/mx-linux/best_release.json"
FILE_NAME = "MX-[[VER]]_x64.iso"


class MXLinux(GenericUpdater):
    """
    Updater for MX Linux.
    
    MX Linux hosts releases on SourceForge which has a convenient API.
    """
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
        
        # Get latest release info from SourceForge API
        response = requests.get(SOURCEFORGE_API)
        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch release info from SourceForge API"
            )
        
        self.release_info = response.json()
    
    @cache
    def _get_latest_version(self) -> list[str]:
        """Extract version from the release filename."""
        filename = self.release_info.get('release', {}).get('filename', '')
        # MX filenames look like: MX-23.1_x64.iso
        match = re.search(r'MX-(\d+(?:\.\d+)*)', filename)
        if match:
            return self._str_to_version(match.group(1))
        raise VersionNotFoundError("Could not parse version from SourceForge release")
    
    @cache
    def _get_download_link(self) -> str:
        """Get the download URL from SourceForge."""
        url = self.release_info.get('release', {}).get('url', '')
        if not url:
            raise VersionNotFoundError("No download URL found in SourceForge API")
        
        # Convert to direct download URL
        return url.replace('/files/', '/files/download/')
    
    def check_integrity(self) -> bool:
        # MX Linux provides MD5 checksums on their download page
        # TODO: Implement checksum verification
        return True
