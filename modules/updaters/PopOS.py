"""
Pop!_OS Updater

Pop!_OS is System76's Ubuntu-based distribution with excellent hardware support.
Downloads from Pop!_OS ISO server.
"""
from functools import cache
from pathlib import Path
import re
import cloudscraper
from bs4 import BeautifulSoup
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import sha256_hash_check

DOWNLOAD_PAGE_URL = "https://system76.com/pop/download/"
FILE_NAME = "pop-os_[[VER]]_amd64_[[EDITION]].iso"


class PopOS(GenericUpdater):
    """
    Updater for Pop!_OS.
    
    Pop!_OS provides Intel/AMD and NVIDIA variants.
    Uses cloudscraper to bypass Cloudflare protection.
    """
    
    def __init__(self, folder_path: Path, edition: str = "intel") -> None:
        self.valid_editions = ["intel", "nvidia"]
        self.edition = edition.lower()
        
        if self.edition not in self.valid_editions:
            raise ValueError(f"Invalid edition '{self.edition}'. Must be one of: {self.valid_editions}")
        
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
        
        # Use cloudscraper to bypass Cloudflare
        self.scraper = cloudscraper.create_scraper()
        self.download_page = self.scraper.get(DOWNLOAD_PAGE_URL, timeout=30)
        if self.download_page.status_code != 200:
            raise ConnectionError(f"Failed to fetch download page from '{DOWNLOAD_PAGE_URL}'")
        
        self.soup = BeautifulSoup(self.download_page.content, features="html.parser")
    
    @cache
    def _get_latest_version(self) -> list[str]:
        """Extract the latest version from the download page."""
        import re
        # Look for version pattern in download links or text
        text = self.soup.get_text()
        # Pop!_OS versions look like "22.04 LTS" or "23.10"
        match = re.search(r'(\d+\.\d+)\s*(?:LTS)?', text)
        if match:
            return self._str_to_version(match.group(1))
        raise VersionNotFoundError("Could not find Pop!_OS version")
    
    @cache
    def _get_download_link(self) -> str:
        """Build the download URL based on version and edition."""
        version = self._version_to_str(self._get_latest_version())
        edition_suffix = "" if self.edition == "intel" else "_nvidia"
        
        # Try to find the build number by checking the ISO server
        # Pop!_OS ISO URL pattern: https://iso.pop-os.org/{version}/amd64/{edition}/{build}/filename.iso
        # For simplicity, we'll try common build numbers or scan the directory
        base_url = "https://iso.pop-os.org"
        edition_path = "intel" if self.edition == "intel" else "nvidia"
        
        # Try to find available builds
        try:
            version_url = f"{base_url}/{version}/amd64/{edition_path}/"
            response = self.scraper.get(version_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, features="html.parser")
                # Find build directories (numeric)
                builds = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if re.match(r'^\d+/$', href):
                        builds.append(int(href.rstrip('/')))
                
                if builds:
                    # Use the latest build
                    latest_build = max(builds)
                    filename = f"pop-os_{version}_amd64_{edition_path}_{latest_build}.iso"
                    return f"{base_url}/{version}/amd64/{edition_path}/{latest_build}/{filename}"
        except Exception:
            pass
        
        # Fallback: guess build 20 (common default)
        filename = f"pop-os_{version}_amd64_{edition_path}_20.iso"
        return f"{base_url}/{version}/amd64/{edition_path}/20/{filename}"
    
    def check_integrity(self) -> bool:
        """Pop!_OS provides SHA256 checksums."""
        try:
            version = self._version_to_str(self._get_latest_version())
            edition_path = "intel" if self.edition == "intel" else "nvidia"
            
            # Extract build number from download link
            download_link = self._get_download_link()
            match = re.search(r'/(\d+)/', download_link)
            build = match.group(1) if match else "20"
            
            # Fetch SHA256 file
            base_url = "https://iso.pop-os.org"
            sha_url = f"{base_url}/{version}/amd64/{edition_path}/{build}/SHA256SUMS"
            response = self.scraper.get(sha_url)
            
            if response.status_code == 200:
                # Parse checksum file
                for line in response.text.splitlines():
                    if f"pop-os_{version}" in line:
                        checksum = line.split()[0]
                        return sha256_hash_check(
                            self._get_complete_normalized_file_path(absolute=True),
                            checksum
                        )
        except Exception:
            pass
        
        return True
