import tempfile
from pathlib import Path

from modules.mirrors.Clonezilla.ClonezillaVersion import ClonezillaVersion
from modules.mirrors.GenericComplexMirror import GenericComplexMirror
from modules.SumType import SumType
from modules.utils import parse_hash, pgp_receive_key


class SourceForge(GenericComplexMirror):
    # From https://clonezilla.org/gpg-verify.php
    KEY_ID = "667857D045599AFD"
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self) -> None:
        checksum_page_url: str = (
            "https://clonezilla.org/downloads/stable/data/CHECKSUMS.TXT"
        )
        super().__init__(
            url=checksum_page_url,
            version_regex=r"clonezilla-live-(.+)-amd64.iso",
            version_class=ClonezillaVersion,
        )

    def initialize(self) -> None:
        super().initialize()

        tmp = tempfile.NamedTemporaryFile(delete=False, prefix="sisou_", mode="w")
        tmp.write(self._text_page)
        tmp.flush()
        tmp.close()

        self._signature_file = Path(tmp.name)

    def __del__(self):
        if self._signature_file:
            self._signature_file.unlink(missing_ok=True)

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        cur_sum_type: SumType | None = None
        sums: list[str] = []
        sum_types: list[SumType] = []
        for line in self._text_page.splitlines():
            if line.startswith("#"):
                for sum_type in SumType:
                    if sum_type.value in line:
                        cur_sum_type = sum_type
                        break
                continue
            if not cur_sum_type:
                continue
            sum_types.append(cur_sum_type)
            sums.append(parse_hash(line, self._file_regex, 0))
        return sum_types, sums

    def _get_download_link(self) -> str:
        return f"https://sourceforge.net/projects/clonezilla/files/clonezilla_live_stable/{self.version}/clonezilla-live-{self.version}-amd64.iso"

    def _get_signature(self) -> bytes | None:
        r = self.session.get(
            "https://clonezilla.org/downloads/stable/data/CHECKSUMS.TXT.gpg"
        )
        r.raise_for_status
        return r.content

    def _get_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)

    def download_and_verify(self, file: Path) -> bool:
        return_val = super().download_and_verify(file)
        if self._signature_file:
            self._signature_file.unlink(missing_ok=True)
        return return_val
