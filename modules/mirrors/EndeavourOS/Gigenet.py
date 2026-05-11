from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import pgp_receive_key


class Gigenet(GenericHTTPMirror):
    # https://discovery.endeavouros.com/signature-and-keyring/how-to-check-and-trust-key-and-signature-for-the-endeavouros-iso/
    KEY_ID = "8F43FC374CD4CEEA19CEE323E3D8752ACDF595A1"
    KEY_SERVER = "keyserver.ubuntu.com"

    def __init__(self) -> None:
        super().__init__(
            uri="https://mirrors.gigenet.com/endeavouros/iso/",
            download_regex=r"EndeavourOS_[\w-]+-([\d\.]+).iso",
            version_regex=r"EndeavourOS_[\w-]+-([\d\.]+).iso",
        )

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
