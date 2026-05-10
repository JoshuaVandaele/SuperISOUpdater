from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp


class KaliLinuxHTTP(GenericHTTPMirror):
    def __init__(self, arch: str, edition: str) -> None:
        super().__init__(
            uri="https://cdimage.kali.org/current/",
            download_regex=rf"kali-linux-([\d\.]+)-{edition}-{arch}\.iso",
            version_regex=rf"kali-linux-([\d\.]+)-{edition}-{arch}\.iso",
            signed_file=download_file_to_tmp(
                "https://cdimage.kali.org/current/SHA256SUMS"
            ),
        )

    def _determine_signature(self) -> bytes:
        r = self.session.get(f"{self.uri}/SHA256SUMS.gpg")
        r.raise_for_status()
        return r.content

    def _determine_public_key(self) -> bytes | None:
        # https://www.kali.org/docs/introduction/download-official-kali-linux-images/#verifying-your-downloaded-kali-image
        r = self.session.get("https://archive.kali.org/archive-key.asc")
        r.raise_for_status()
        return r.content
