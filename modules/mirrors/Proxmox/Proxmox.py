from modules.Checksum import SHA256Sum
from modules.DotDashVersion import DotDashVersion
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import parse_hash


class Proxmox(GenericHTTPMirror):
    def __init__(self, edition: str) -> None:
        super().__init__(
            uri="https://enterprise.proxmox.com/iso/",
            download_regex=rf"proxmox-{edition}_(.+)\.iso",
            version_regex=rf"proxmox-{edition}_(.+)\.iso",
            version_class=DotDashVersion,
        )

    def _determine_public_key(self) -> bytes:
        # https://enterprise.proxmox.com/iso/#verify
        r = self.session.get(
            "https://enterprise.proxmox.com/debian/proxmox-archive-keyring-trixie.gpg"
        )
        r.raise_for_status()
        return r.content

    def _determine_signature(self) -> bytes | None:
        r = self.session.get(f"{self.download_link}.asc")
        r.raise_for_status()
        return r.content

    def _determine_sums(self):
        r = self.session.get(f"{self.download_link}.sha256")
        r.raise_for_status()
        return [SHA256Sum(parse_hash(r.text, self._download_regex, 0))]
