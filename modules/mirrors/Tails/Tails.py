from modules.Checksum import Checksum, SumType
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror


class Tails(GenericHTTPMirror):
    def __init__(self, arch: str) -> None:
        self.arch = arch
        super().__init__(
            uri="https://tails.net/install/download/index.en.html",
            file_regex=rf"tails-{arch}-(.+?).img",
            version_regex=rf"tails-{arch}-([\d.]+)",
        )

    def _determine_sums(self) -> list[Checksum]:
        sum_file = self.session.get(
            f"https://tails.net/install/v2/Tails/{self.arch}/stable/latest.json",
            headers=self.headers,
        )
        sum_file.raise_for_status()
        sum_json = sum_file.json()

        sums: list[Checksum] = []
        installations = sum_json.get("installations") if sum_json else []
        for installation in installations:
            for ipath in installation.get("installation-paths", []):
                for tfile in ipath.get("target-files", []):
                    if tfile.get("url") != self.download_link:
                        continue
                    for key, value in tfile.items():
                        for sum_type in SumType:
                            if sum_type.matches(key):
                                sums.append(Checksum.from_sum_type(sum_type, value))

        if sums:
            return sums

        raise ValueError(
            "Could not determine the checksum from "
            "https://tails.net/install/v2/Tails/amd64/stable/latest.json"
        )
