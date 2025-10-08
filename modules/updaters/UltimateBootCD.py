from functools import cache
from pathlib import Path
from random import shuffle
import requests
from bs4 import BeautifulSoup
from modules.exceptions import VersionNotFoundError
from modules.updaters.GenericUpdater import GenericUpdater

MIRRORS = [
    "https://mirror.clientvps.com/ubcd",
    "http://mirror.koddos.net/ubcd",
    "https://mirror.lyrahosting.com/ubcd",
]
FILE_NAME = "ubcd[[VER]].iso"

class UltimateBootCD(GenericUpdater):
    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        mirrors = MIRRORS.copy()
        shuffle(mirrors)

        self.mirror = None
        self.download_link = None
        for mirror in mirrors:
            try:
                resp = requests.get(mirror)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, features="html.parser")
                    iso_links = [a.get("href") for a in soup.find_all("a", href=True) if a.get("href", "").endswith(".iso")]
                    if iso_links:
                        # Sort ISO filenames by version number, descending
                        latest_iso = sorted(iso_links, key=lambda x: int("".join(filter(str.isdigit, x))), reverse=True)[0]
                        self.mirror = mirror
                        self.download_link = mirror.rstrip("/") + "/" + latest_iso.lstrip("/")
                        break
            except Exception:
                continue
        if not self.download_link:
            raise ConnectionError("Could not find a valid ISO in any mirror!")

    @cache
    def _get_latest_version(self):
        # Extract version number from the latest ISO filename, e.g. ubcd539.iso -> '539'
        if self.download_link:
            import re
            match = re.search(r'ubcd(\d+)\.iso', self.download_link)
            if match:
                return match.group(1)
        raise VersionNotFoundError("Could not determine latest UBCD version from download link.")

    @cache
    def _get_download_link(self) -> str:
        return self.download_link

    def check_integrity(self) -> bool:
        # TODO: Implement .md5 or .sha256 check from mirror if needed
        return True
