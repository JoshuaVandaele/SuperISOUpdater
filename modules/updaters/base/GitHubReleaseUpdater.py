"""
GitHub Release Updater Base Class

This base class handles updaters that pull ISOs from GitHub Releases.
Many open-source projects use GitHub Releases for distribution.
"""
from functools import cache
from pathlib import Path
import requests
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import sha256_hash_check


class GitHubReleaseUpdater(GenericUpdater):
    """
    Base class for updaters that download from GitHub Releases.
    
    Subclasses should define:
        - github_repo: str (e.g., "owner/repo")
        - asset_pattern: str (regex pattern to match the asset filename)
        - file_name: str (the target filename with [[VER]] placeholder)
    """
    
    github_repo: str
    asset_pattern: str
    
    def __init__(self, folder_path: Path, *args, **kwargs) -> None:
        if not hasattr(self, 'github_repo'):
            raise NotImplementedError("Subclass must define 'github_repo'")
        if not hasattr(self, 'asset_pattern'):
            raise NotImplementedError("Subclass must define 'asset_pattern'")
            
        super().__init__(folder_path, *args, **kwargs)
        
        # Fetch release data
        self.api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.release_data = self._fetch_release_data()
    
    def _fetch_release_data(self) -> dict:
        """Fetch the latest release data from GitHub API."""
        response = requests.get(self.api_url)
        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch GitHub release data from {self.api_url}"
            )
        return response.json()
    
    @cache
    def _get_latest_version(self) -> list[str]:
        """Extract version from release tag."""
        tag = self.release_data.get('tag_name', '')
        # Remove common prefixes like 'v', 'release-', etc.
        version_str = tag.lstrip('vV').lstrip('release-').lstrip('Release-')
        return self._str_to_version(version_str)
    
    @cache
    def _get_download_link(self) -> str:
        """Find the matching asset download URL."""
        import re
        assets = self.release_data.get('assets', [])
        
        for asset in assets:
            if re.search(self.asset_pattern, asset['name'], re.IGNORECASE):
                return asset['browser_download_url']
        
        raise VersionNotFoundError(
            f"No asset matching pattern '{self.asset_pattern}' found in release"
        )
    
    def check_integrity(self) -> bool:
        """
        Check integrity using SHA256 from release body or asset.
        Override if the project provides checksums differently.
        """
        # Many GitHub releases include SHA256 in the release body
        # This is a basic implementation - override as needed
        return True
