from modules.Checksum import Checksum, SHA256Sum, SHA512Sum
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror


class Fastly(GenericHTTPMirror):
    def __init__(self, arch: str) -> None:
        super().__init__(
            # TODO: It would be better the uri was from Fastly directly
            uri="https://www.system-rescue.org/Download/",
            download_regex=rf"systemrescue-.+\-{arch}\.iso",
            version_regex=rf"systemrescue-(.+?)-{arch}\.iso",
        )

    def _determine_download_link(self) -> str:
        return f"https://fastly-cdn.system-rescue.org/releases/{self.version}/systemrescue-{self.version}-amd64.iso"

    def _determine_sums(self) -> list[Checksum]:
        r_sha256 = self.session.get(f"{self._determine_download_link()}.sha256")
        r_sha512 = self.session.get(f"{self._determine_download_link()}.sha512")
        r_sha256.raise_for_status()
        r_sha512.raise_for_status()
        sha256 = r_sha256.text.split()[0]
        sha512 = r_sha512.text.split()[0]
        return [SHA256Sum(sha256), SHA512Sum(sha512)]

    def _determine_signature(self) -> bytes | None:
        r = self.session.get(f"{self._determine_download_link()}.asc")
        r.raise_for_status()
        return r.content
