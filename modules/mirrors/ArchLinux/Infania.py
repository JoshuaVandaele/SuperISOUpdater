from modules.mirrors.GenericMirror import GenericMirror
from modules.utils import pgp_receive_key


class Infania(GenericMirror):
    KEY_ID = "3E80CA1A8B89F69CBA57D98A76A5EF9054449A5C"
    KEY_SERVER = "keyserver.ubuntu.com"

    def __init__(self) -> None:
        super().__init__(
            url="https://ftpmirror.infania.net/mirror/archlinux/iso/latest/",
            file_regex=r"archlinux-.+-x86_64\.iso",
            version_regex=r"archlinux-(.+)-x86_64\.iso",
            version_padding=2,
        )

    def _get_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
