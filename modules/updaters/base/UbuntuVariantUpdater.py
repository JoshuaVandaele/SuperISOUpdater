"""
Ubuntu Variant Base Updater

Base class for official Ubuntu flavors (Xubuntu, Kubuntu, Lubuntu, etc.)
All use the same release structure from cdimage.ubuntu.com
"""
from functools import cache
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater


class UbuntuVariantUpdater(GenericUpdater):
    """
    Base class for Ubuntu official flavors.
    
    Subclasses should define:
        - variant_name: str (lowercase: xubuntu, kubuntu, etc.)
        - file_name_template: str (with [[VER]] placeholder)
    """
    
    variant_name: str
    file_name_template: str
    
    def __init__(self, file_path: Path) -> None:
        if not hasattr(self, 'variant_name'):
            raise NotImplementedError("Subclass must define 'variant_name'")
        if not hasattr(self, 'file_name_template'):
            raise NotImplementedError("Subclass must define 'file_name_template'")
            
        super().__init__(file_path)
        
        # Fetch the releases page
        self.releases_url = f"https://cdimage.ubuntu.com/{self.variant_name}/releases/"
        self.download_page = requests.get(self.releases_url, timeout=30)
        
        if self.download_page.status_code != 200:
            raise ConnectionError(f"Failed to fetch releases from '{self.releases_url}'")
        
        self.soup = BeautifulSoup(self.download_page.content, features="html.parser")
    
    @cache
    def _get_latest_version(self) -> list[str]:
        """Find the latest LTS or stable release version."""
        # Look for version directories like "22.04/", "24.04/", etc.
        version_pattern = re.compile(r'^(\d+\.\d+)/$')
        versions = []
        
        for link in self.soup.find_all('a', href=True):
            href = link.get('href', '')
            match = version_pattern.match(href)
            if match:
                version_str = match.group(1)
                # Check if the release actually has files by trying to access it
                release_url = f"{self.releases_url}{version_str}/release/"
                try:
                    response = requests.head(release_url, timeout=5)
                    if response.status_code == 200:
                        versions.append(self._str_to_version(version_str))
                except:
                    continue
        
        if not versions:
            raise VersionNotFoundError(f"Could not find any {self.variant_name} versions")
        
        # Return the latest version
        return sorted(versions, reverse=True)[0]
    
    @cache
    def _get_download_link(self) -> str:
        """Build the download URL for the latest release."""
        version = self._version_to_str(self._get_latest_version())
        
        # Ubuntu variants use: /variant/releases/VERSION/release/variant-VERSION-desktop-amd64.iso
        release_url = f"{self.releases_url}{version}/release/"
        
        # Try to get the actual ISO filename from the release page
        try:
            response = requests.get(release_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, features="html.parser")
                
                # Find the desktop amd64 ISO
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if (href.endswith('.iso') and 
                        'desktop' in href.lower() and 
                        'amd64' in href.lower() and
                        not href.endswith('.iso.torrent')):
                        return f"{release_url}{href}"
        except Exception:
            pass
        
        # Fallback: construct the expected filename
        filename = self.file_name_template.replace('[[VER]]', version)
        return f"{release_url}{filename}"
    
    def check_integrity(self) -> bool:
        """Ubuntu provides SHA256SUMS files."""
        # TODO: Implement SHA256 verification from SHA256SUMS file
        return True
