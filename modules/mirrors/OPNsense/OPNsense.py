import bz2
import re
import shutil
from pathlib import Path

import requests_cache
from bs4 import BeautifulSoup

from modules.exceptions import IntegrityCheckError
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.Version import Version


class OPNsense(GenericHTTPMirror):
    def __init__(self, arch: str, edition: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        version = self._determine_latest_version()

        super().__init__(
            uri=f"https://pkg.opnsense.org/releases/{version}/",
            download_regex=rf"OPNsense-{version}-{edition}-{arch}\.i(so|mg)\.bz2",
            version=version,
            # TODO: Support OpenSSL signatures/verification
            has_signature=False,
        )

    def _determine_latest_version(self) -> Version:
        r = self.session.get(
            "https://pkg.opnsense.org/releases/",
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features="html.parser")
        urls = [str(a_tag.get("href")) for a_tag in soup.find_all("a", href=True)]

        latest_version = Version("0")
        for url in urls:
            ver_match = re.match(r"^((\d+\.)+\d+)", url)
            if not ver_match:
                continue
            current_version = Version(ver_match.group(0))
            if current_version and current_version > latest_version:
                latest_version = current_version

        if latest_version == Version("0"):
            raise ValueError(f"No version found on the page '{r.url}'")
        return latest_version

    def download_and_verify(self, file) -> None:
        bz2_file = Path(f"{file}.bz2")
        super().download_and_verify(bz2_file)
        try:
            with bz2.open(bz2_file, "rb") as f_in, open(file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            raise IntegrityCheckError(f"Failed to extract {bz2_file}") from e
        finally:
            bz2_file.unlink(missing_ok=True)

    def _fetch_and_parse_sum(self, url: str) -> tuple[str, int]:
        text, _ = super()._fetch_and_parse_sum(url)
        return text, -1
