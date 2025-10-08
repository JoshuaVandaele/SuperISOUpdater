"""
Parrot Security OS Updater

Parrot is a popular security and forensics Linux distribution.
Downloads from Parrot's official ISO mirror.
"""
from pathlib import Path
from modules.updaters.base.DirectMirrorUpdater import DirectMirrorUpdater

FILE_NAME = "Parrot-security-[[VER]]_amd64.iso"


class ParrotSecurity(DirectMirrorUpdater):
    """
    Updater for Parrot Security OS.
    
    Parrot provides ISO downloads via their official Debian mirror.
    """
    
    mirrors = [
        "https://deb.parrot.sh/parrot/iso/",
    ]
    
    iso_pattern = r"Parrot-security-[\d.]+_amd64\.iso$"
    
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)
    
    def _scan_mirrors(self) -> None:
        """
        Override to handle Parrot's version-based directory structure.
        Need to find latest version directory first, then scan for ISO.
        """
        import re
        from random import shuffle
        import requests
        from bs4 import BeautifulSoup
        
        mirrors = self.mirrors.copy()
        shuffle(mirrors)
        
        for mirror in mirrors:
            try:
                response = requests.get(mirror, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find version directories (e.g., "6.4/")
                version_dirs = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    # Match version pattern like "6.4/"
                    if re.match(r'^\d+\.\d+/$', href):
                        version_dirs.append(href.rstrip('/'))
                
                if not version_dirs:
                    continue
                
                # Sort to get latest version
                latest_version = sorted(
                    version_dirs,
                    key=lambda v: [int(x) for x in v.split('.')],
                    reverse=True
                )[0]
                
                # Now scan the version directory for ISOs
                version_url = f"{mirror}{latest_version}/"
                response = requests.get(version_url, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                iso_links = []
                
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if re.search(self.iso_pattern, href):
                        iso_links.append(href)
                
                if iso_links:
                    latest_iso = self._select_latest_iso(iso_links)
                    self.mirror = mirror
                    self.download_link = f"{version_url}{latest_iso}"
                    return
                    
            except Exception:
                continue
        
        raise ConnectionError("Could not find a valid ISO in any mirror!")
    
    def check_integrity(self) -> bool:
        """Parrot provides .hashes file with checksums."""
        # TODO: Implement hash verification from .hashes file
        return True
