from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import pgp_receive_key


class ArkHost(GenericHTTPMirror):
    KEY_ID = "A574A1915CEDE31A3BFF5A68606520ACB886B428"
    KEY_SERVER = "pgpkeys.eu"

    def __init__(self, edition, arch) -> None:
        super().__init__(
            uri="https://artix.arkhost.com/iso/",
            download_regex=rf"artix-{edition}-\d+-{arch}\.iso",
            version_regex=rf"artix-{edition}-(\d+)-{arch}\.iso",
            version_separator="",
        )

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
