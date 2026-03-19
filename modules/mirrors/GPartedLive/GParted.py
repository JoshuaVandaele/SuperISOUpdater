import re

import requests_cache

from modules.DotDashVersion import DotDashVersion
from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType
from modules.utils import create_sig_check_file_from_url, parse_hash, pgp_receive_key

CHECKSUM_URL: str = "https://gparted.org/gparted-live/stable/CHECKSUMS.TXT"


class GParted(GenericMirror):
    KEY_ID = "EB1DD5BF6F88820BBCF5356C8E94C9CD163E3FB0"
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self, arch: str) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        super().__init__(
            url="https://gparted.org/download.php",
            file_regex=rf"gparted-live-.+-{arch}\.iso",
            version_regex=rf"gparted-live-(.+?)-{arch}\.iso",
            version_class=DotDashVersion,
            signature_file=create_sig_check_file_from_url(CHECKSUM_URL),
        )

    def _get_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        r = self.session.get(CHECKSUM_URL)
        r.raise_for_status()
        cur_sum_type: SumType | None = None
        sums: list[str] = []
        sum_types: list[SumType] = []
        for line in r.text.lower().splitlines():
            if line.startswith("#"):
                for sum_type in SumType:
                    if sum_type.value in line:
                        cur_sum_type = sum_type
                        break
                continue
            if not cur_sum_type:
                continue
            if not re.search(self._file_regex, line):
                cur_sum_type = None
                continue
            sum_types.append(cur_sum_type)
            sums.append(parse_hash(line, self._file_regex, 0))
            cur_sum_type = None
        return sum_types, sums
