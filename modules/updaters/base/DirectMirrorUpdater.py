"""
Direct Mirror Updater Base Class

This base class handles updaters that scrape directory listings from mirrors.
Similar to the UltimateBootCD pattern we just implemented.
"""
from functools import cache
from pathlib import Path
from random import shuffle
import requests
from bs4 import BeautifulSoup
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater


class DirectMirrorUpdater(GenericUpdater):
    """
    Base class for updaters that download from directory listing mirrors.
    
    Subclasses should define:
        - mirrors: list[str] (list of mirror URLs)
        - iso_pattern: str (regex pattern to match ISO files)
    """
    
    mirrors: list[str]
    iso_pattern: str
    
    def __init__(self, folder_path: Path, *args, **kwargs) -> None:
        if not hasattr(self, 'mirrors'):
            raise NotImplementedError("Subclass must define 'mirrors'")
        if not hasattr(self, 'iso_pattern'):
            raise NotImplementedError("Subclass must define 'iso_pattern'")
            
        super().__init__(folder_path, *args, **kwargs)
        
        # Find working mirror and latest ISO
        self.mirror = None
        self.download_link = None
        self._scan_mirrors()
    
    def _scan_mirrors(self) -> None:
        """Scan mirrors to find the latest ISO."""
        import re
        mirrors = self.mirrors.copy()
        shuffle(mirrors)
        
        for mirror in mirrors:
            try:
                resp = requests.get(mirror, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, features="html.parser")
                    iso_links = [
                        a.get("href") 
                        for a in soup.find_all("a", href=True) 
                        if re.search(self.iso_pattern, a.get("href", ""), re.IGNORECASE)
                    ]
                    
                    if iso_links:
                        # Sort by version and get latest
                        latest_iso = self._select_latest_iso(iso_links)
                        self.mirror = mirror
                        self.download_link = mirror.rstrip("/") + "/" + latest_iso.lstrip("/")
                        return
            except Exception as e:
                continue
        
        if not self.download_link:
            raise ConnectionError("Could not find a valid ISO in any mirror!")
    
    def _select_latest_iso(self, iso_links: list[str]) -> str:
        """
        Select the latest ISO from a list of filenames.
        Override this method for custom sorting logic.
        """
        # Default: sort by numeric version in filename
        return sorted(
            iso_links, 
            key=lambda x: int("".join(filter(str.isdigit, x)) or "0"), 
            reverse=True
        )[0]
    
    @cache
    def _get_latest_version(self):
        """Extract version number from the download link."""
        import re
        if self.download_link:
            match = re.search(r'(\d+(?:\.\d+)*)', self.download_link)
            if match:
                return match.group(1)
        raise VersionNotFoundError("Could not determine version from download link.")
    
    @cache
    def _get_download_link(self) -> str:
        return self.download_link
    
    def check_integrity(self) -> bool:
        """
        Override to implement checksum validation.
        Many mirrors provide .md5 or .sha256 files alongside ISOs.
        """
        return True
