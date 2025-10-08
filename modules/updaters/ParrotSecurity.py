"""
Parrot Security OS Updater

Parrot is a popular security and forensics Linux distribution.
Downloads from SourceForge mirrors.
"""
from functools import cache
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater

DOWNLOAD_PAGE_URL = "https://www.parrotsec.org/download/"
FILE_NAME = "Parrot-security-[[VER]]_amd64.iso"


class ParrotSecurity(GenericUpdater):
    """
    Updater for Parrot Security OS.
    
    Parrot provides ISO downloads via their download page and mirrors.
    """
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
        
        self.download_page = requests.get(DOWNLOAD_PAGE_URL)
        if self.download_page.status_code != 200:
            raise ConnectionError(
                f"Failed to fetch download page from '{DOWNLOAD_PAGE_URL}'"
            )
        
        self.soup = BeautifulSoup(self.download_page.content, features="html.parser")
    
    @cache
    def _get_latest_version(self) -> list[str]:
        """Extract the latest version from the download page."""
        # Look for version in page text or links
        import re
        text = self.soup.get_text()
        # Parrot versions typically look like "5.3" or "6.0"
        match = re.search(r'Parrot\s+(?:OS\s+)?(\d+\.\d+)', text, re.IGNORECASE)
        if match:
            return self._str_to_version(match.group(1))
        raise VersionNotFoundError("Could not find Parrot version on download page")
    
    @cache
    def _get_download_link(self) -> str:
        """Find the security edition download link."""
        # Parrot typically has direct download links or redirects to SourceForge
        links = self.soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            if "security" in href.lower() and href.endswith(".iso"):
                return href
            # SourceForge pattern
            if "sourceforge.net" in href and "security" in href.lower():
                return href
        
        raise VersionNotFoundError("Could not find download link for Parrot Security")
    
    def check_integrity(self) -> bool:
        # TODO: Implement SHA256 check from Parrot's checksums page
        return True
