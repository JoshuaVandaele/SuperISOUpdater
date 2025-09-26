from modules.mirrors.Clonezilla.ClonezillaVersion import ClonezillaVersion
from modules.mirrors.GenericComplexMirror import GenericComplexMirror
from modules.SumType import SumType
from modules.utils import parse_hash


class SourceForge(GenericComplexMirror):
    def __init__(self) -> None:
        super().__init__(
            url=f"https://clonezilla.org/downloads/stable/data/CHECKSUMS.TXT",
            version_regex=r"clonezilla-live-(.+)-amd64.iso",
            version_class=ClonezillaVersion,
        )

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
