from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import download_file_to_tmp, pgp_receive_key


class Kernel(GenericHTTPMirror):
    # https://linuxmint-installation-guide.readthedocs.io/en/latest/verify.html
    KEY_ID = "27DEB15644C6B3CF3BD7D291300F846BA25BAE09"
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self, edition: str) -> None:
        checksum_url: str = (
            "https://mirrors.edge.kernel.org/linuxmint/debian/sha256sum.txt"
        )

        super().__init__(
            uri="https://mirrors.edge.kernel.org/linuxmint/debian/",
            download_regex=rf"lmde-([\d\.]+)-{edition}-64bit.iso",
            version_regex=rf"lmde-([\d\.]+)-{edition}-64bit.iso",
            signed_file=download_file_to_tmp(checksum_url),
        )

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
