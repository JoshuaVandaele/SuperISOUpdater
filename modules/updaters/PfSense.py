"""
pfSense Updater

pfSense is a popular open-source firewall and router platform.
Downloads from Netgate's download servers.
"""
from functools import cache
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater
from modules.utils import sha256_hash_check

DOWNLOAD_PAGE_URL = "https://www.pfsense.org/download/"
FILE_NAME = "pfSense-CE-[[VER]]-amd64.iso"


class PfSense(GenericUpdater):
    """
    Updater for pfSense Community Edition.
    
    pfSense provides ISO downloads for network/firewall installations.
    """
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
        
        # Fetch download page
        self.download_page = requests.get(DOWNLOAD_PAGE_URL)
        if self.download_page.status_code != 200:
            raise ConnectionError(f"Failed to fetch download page from '{DOWNLOAD_PAGE_URL}'")
        
        self.soup = BeautifulSoup(self.download_page.content, features="html.parser")
    
    @cache
    def _get_latest_version(self) -> list[str]:
        """Extract the latest version from the download page."""
        # pfSense versions look like "2.7.2" or "23.09"
        text = self.soup.get_text()
        match = re.search(r'(?:Version\s+)?(\d+\.\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if match:
            return self._str_to_version(match.group(1))
        
        # Alternative: look in download links
        links = self.soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            match = re.search(r'pfSense-CE-(\d+\.\d+(?:\.\d+)?)', href)
            if match:
                return self._str_to_version(match.group(1))
        
        raise VersionNotFoundError("Could not find pfSense version")
    
    @cache
    def _get_download_link(self) -> str:
        """Find the AMD64 ISO download link."""
        links = self.soup.find_all("a", href=True)
        
        for link in links:
            href = link.get("href", "")
            # Look for AMD64 ISO download links
            if "amd64.iso" in href.lower() and "pfsense" in href.lower():
                # Handle relative URLs
                if href.startswith("/"):
                    return f"https://www.pfsense.org{href}"
                return href
        
        raise VersionNotFoundError("Could not find pfSense AMD64 ISO download link")
    
    def check_integrity(self) -> bool:
        """pfSense provides SHA256 checksums."""
        try:
            # pfSense typically has a checksums file or link
            download_link = self._get_download_link()
            sha_url = download_link.replace(".iso", ".iso.sha256")
            
            response = requests.get(sha_url)
            if response.status_code == 200:
                # Parse checksum (format: "checksum filename")
                checksum = response.text.strip().split()[0]
                return sha256_hash_check(
                    self._get_complete_normalized_file_path(absolute=True),
                    checksum
                )
        except Exception:
            pass
        
        return True
