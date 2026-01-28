import re
import tempfile
from pathlib import Path

import requests_cache

from modules.mirrors.Clonezilla.ClonezillaVersion import ClonezillaVersion
from modules.mirrors.GenericComplexMirror import GenericComplexMirror
from modules.SumType import SumType
from modules.utils import parse_hash, pgp_receive_key

CHECKSUM_URL: str = "https://clonezilla.org/downloads/stable/data/CHECKSUMS.TXT"


class SourceForge(GenericComplexMirror):
    # From https://clonezilla.org/gpg-verify.php
    KEY_ID = "667857D045599AFD"
    KEY_SERVER = "keys.openpgp.org"

    def create_sig_check_file(self) -> Path:
        r = self.session.get(CHECKSUM_URL)
        r.raise_for_status()

        sig_file = tempfile.NamedTemporaryFile(delete=False, prefix="sisou_", mode="wb")
        sig_file.write(r.content)
        sig_file.flush()
        sig_file.close()

        return Path(tempfile.gettempdir()) / sig_file.name

    def __init__(self, arch) -> None:
        self.session = requests_cache.CachedSession(backend="memory")
        super().__init__(
            url=CHECKSUM_URL,
            version_regex=rf"clonezilla-live-(.+)-{arch}.iso",
            version_class=ClonezillaVersion,
            signature_file=self.create_sig_check_file(),
        )
        self.arch = arch

    def __del__(self):
        if self._signature_file:
            self._signature_file.unlink(missing_ok=True)

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        cur_sum_type: SumType | None = None
        sums: list[str] = []
        sum_types: list[SumType] = []
        for line in self._text_page.lower().splitlines():
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

    def _get_download_link(self) -> str:
        return f"https://sourceforge.net/projects/clonezilla/files/clonezilla_live_stable/{self.version}/clonezilla-live-{self.version}-{self.arch}.iso"

    def _get_signature(self) -> bytes:
        r = self.session.get(f"{CHECKSUM_URL}.gpg")
        r.raise_for_status()
        return r.content

    def _get_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
