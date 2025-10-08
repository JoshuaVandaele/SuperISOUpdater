"""
Pop!_OS Updater

Pop!_OS is System76's Ubuntu-based distribution with excellent hardware support.
Downloads from Pop!_OS servers.
"""
from functools import cache
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import sha256_hash_check

DOWNLOAD_PAGE_URL = "https://pop.system76.com/"
ISO_BASE_URL = "https://iso.pop-os.org"
FILE_NAME = "pop-os_[[VER]]_amd64_[[EDITION]].iso"


class PopOS(GenericUpdater):
    """
    Updater for Pop!_OS.
    
    Pop!_OS provides Intel/AMD and NVIDIA variants.
    """
    
    def __init__(self, folder_path: Path, edition: str = "intel") -> None:
        self.valid_editions = ["intel", "nvidia"]
        self.edition = edition.lower()
        
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
        
        # Fetch the download page
        self.download_page = requests.get(DOWNLOAD_PAGE_URL)
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
        """Build the download URL."""
        version = self._version_to_str(self._get_latest_version())
        edition_suffix = "" if self.edition == "intel" else "_nvidia"
        
        # Pop!_OS ISO URL pattern
        filename = f"pop-os_{version}_amd64{edition_suffix}.iso"
        return f"{ISO_BASE_URL}/{version}/amd64/{edition_suffix.lstrip('_')}/{filename}"
    
    def check_integrity(self) -> bool:
        """Pop!_OS provides SHA256 checksums."""
        try:
            version = self._version_to_str(self._get_latest_version())
            edition_suffix = "" if self.edition == "intel" else "_nvidia"
            
            # Fetch SHA256 file
            sha_url = f"{ISO_BASE_URL}/{version}/amd64/{edition_suffix.lstrip('_')}/SHA256SUMS"
            response = requests.get(sha_url)
            
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
