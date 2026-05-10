import re

import requests_cache

from modules.Checksum import Checksum, SumType
from modules.DotDashVersion import DotDashVersion
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp, parse_hash, pgp_receive_key

CHECKSUM_URL: str = "https://clonezilla.org/downloads/stable/data/CHECKSUMS.TXT"


class SourceForge(GenericHTTPMirror):
    # From https://clonezilla.org/gpg-verify.php
    KEY_ID = "667857D045599AFD"
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self, arch) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        super().__init__(
            uri=CHECKSUM_URL,
            download_regex=rf"clonezilla-live-([\d\.-]+)-{arch}.iso",
            version_regex=rf"clonezilla-live-([\d\.-]+)-{arch}.iso",
            version_class=DotDashVersion,
            signed_file=download_file_to_tmp(CHECKSUM_URL),
        )
        self.arch = arch

    def __del__(self):
        if self.signed_file:
            self.signed_file.unlink(missing_ok=True)

    def _determine_sums(self) -> list[Checksum]:
        cur_sum_type: SumType | None = None
        sums: list[Checksum] = []
        for line in self._text_page.lower().splitlines():
            if line.startswith("#"):
                for sum_type in SumType:
                    if sum_type.matches(line):
                        cur_sum_type = sum_type
                        break
                continue
            if not cur_sum_type:
                continue
            if not re.search(self._download_regex, line):
                cur_sum_type = None
                continue
            sums.append(
                Checksum.from_sum_type(
                    cur_sum_type, parse_hash(line, self._download_regex, 0)
                )
            )
            cur_sum_type = None
        return sums

    def _determine_download_link(self) -> str:
        return f"https://sourceforge.net/projects/clonezilla/files/clonezilla_live_stable/{self.version}/clonezilla-live-{self.version}-{self.arch}.iso"

    def _determine_signature(self) -> bytes:
        r = self.session.get(f"{CHECKSUM_URL}.gpg")
        r.raise_for_status()
        return r.content

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
