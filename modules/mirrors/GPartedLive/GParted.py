import re

import requests_cache

from modules.Checksum import Checksum, SumType
from modules.DotDashVersion import DotDashVersion
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp, parse_hash, pgp_receive_key

CHECKSUM_URL: str = "https://gparted.org/gparted-live/stable/CHECKSUMS.TXT"


class GParted(GenericHTTPMirror):
    KEY_ID = "EB1DD5BF6F88820BBCF5356C8E94C9CD163E3FB0"
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self, arch: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        super().__init__(
            uri="https://gparted.org/download.php",
            download_regex=rf"gparted-live-.+-{arch}\.iso",
            version_regex=rf"gparted-live-(.+?)-{arch}\.iso",
            version_class=DotDashVersion,
            signed_file=download_file_to_tmp(CHECKSUM_URL),
        )

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)

    def _determine_sums(self) -> list[Checksum]:
        r = self.session.get(CHECKSUM_URL)
        r.raise_for_status()
        cur_sum_type: SumType | None = None
        sums: list[Checksum] = []
        for line in r.text.lower().splitlines():
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
