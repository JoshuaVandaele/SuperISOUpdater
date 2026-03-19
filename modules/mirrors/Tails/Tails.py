from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType


class Tails(GenericMirror):
    def __init__(self, arch: str) -> None:
        self.arch = arch
        super().__init__(
            url="https://tails.net/install/download/index.en.html",
            file_regex=rf"tails-{arch}-(.+?).img",
            version_regex=rf"tails-{arch}-([\d.]+)",
        )

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        sum_file = self.session.get(
            f"https://tails.net/install/v2/Tails/{self.arch}/stable/latest.json",
            headers=self.headers,
        )
        sum_file.raise_for_status()
        sum_json = sum_file.json()

        sums: list[str] = []
        sum_types: list[SumType] = []

        installations = sum_json.get("installations") if sum_json else []
        for installation in installations:
            for ipath in installation.get("installation-paths", []):
                for tfile in ipath.get("target-files", []):
                    if tfile.get("url") != self.download_link:
                        continue
                    for sum_type in SumType:
                        if sum_type.value in tfile:
                            sum_types.append(sum_type)
                            sums.append(tfile[sum_type.value])

        if sum_types and sums:
            return sum_types, sums

        raise ValueError(
            "Could not determine the checksum from "
            "https://tails.net/install/v2/Tails/amd64/stable/latest.json"
        )
