from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType


class Fastly(GenericMirror):
    def __init__(self, arch: str) -> None:
        super().__init__(
            # TODO: It would be better if we could get it from Fastly directly
            url="https://www.system-rescue.org/Download/",
            file_regex=rf"systemrescue-.+\-{arch}\.iso",
            version_regex=rf"systemrescue-(.+?)-{arch}\.iso",
        )

    def _get_download_link(self) -> str:
        return f"https://fastly-cdn.system-rescue.org/releases/{self.version}/systemrescue-{self.version}-amd64.iso"

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        r_sha256 = self.session.get(f"{self._get_download_link()}.sha256")
        r_sha512 = self.session.get(f"{self._get_download_link()}.sha512")
        r_sha256.raise_for_status()
        r_sha512.raise_for_status()
        sha256 = r_sha256.text.split()[0]
        sha512 = r_sha512.text.split()[0]
        sum_types = [SumType.SHA256, SumType.SHA512]
        matches = [sha256, sha512]
        return sum_types, matches

    def _get_signature(self) -> bytes | None:
        r = self.session.get(f"{self._get_download_link()}.asc")
        r.raise_for_status()
        return r.content
