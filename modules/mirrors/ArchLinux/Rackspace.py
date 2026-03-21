from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import pgp_receive_key


class Rackspace(GenericHTTPMirror):
    KEY_ID = "3E80CA1A8B89F69CBA57D98A76A5EF9054449A5C"
    KEY_SERVER = "keyserver.ubuntu.com"

    def __init__(self, arch) -> None:
        super().__init__(
            uri="https://mirror.rackspace.com/archlinux/iso/latest/",
            file_regex=rf"archlinux-.+-{arch}\.iso",
            version_regex=rf"archlinux-(.+)-{arch}\.iso",
            version_padding=2,
        )

    def _determine_public_key(self) -> bytes | None:
        return pgp_receive_key(self.KEY_ID, self.KEY_SERVER)
