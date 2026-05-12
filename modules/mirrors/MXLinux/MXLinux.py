from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import pgp_receive_key


class MXLinux(GenericHTTPMirror):
    KEY_SERVER = "keys.openpgp.org"

    def __init__(self, arch: str, edition: str) -> None:
        self.edition = edition
        regex_edition = edition if edition != "Fluxbox" else "fluxbox"
        uri_edition = edition if edition != "Xfce_ahs" else "Xfce"
        super().__init__(
            uri=f"https://rsync-mxlinux.org/MX/Final/{uri_edition}/",
            download_regex=rf"MX-([\d\.]+)_{regex_edition}_{arch}\.iso",
            version_regex=rf"MX-([\d\.]+)_{regex_edition}_{arch}\.iso",
        )

    def _determine_public_key(self) -> bytes | None:
        # https://mxlinux.org/wiki/system/signed-iso-files/
        match self.edition:
            case "Xfce":
                key_id = "F62EDEAA3AE70A9C99DAC4189B68A1E8B9B6375C"
            case "KDE":
                key_id = "F27753A18E92E3937E6335E770938C780679EE98"
            case "Fluxbox":
                key_id = "4EB6BDCFC6CA16AE8C3471C2409C71B3BCFDED0A"
            case _:
                raise ValueError(f"Unknown edition '{self.edition}'")
        return pgp_receive_key(key_id, self.KEY_SERVER)
