from modules.DotDashVersion import DotDashVersion
from modules.mirrors.GenericMirror import GenericMirror


class Proxmox(GenericMirror):
    def __init__(self, edition: str) -> None:
        super().__init__(
            url="https://enterprise.proxmox.com/iso/",
            file_regex=rf"proxmox-{edition}_(.+)\.iso",
            version_regex=rf"proxmox-{edition}_(.+)\.iso",
            version_class=DotDashVersion,
            # There is a signature, but the key is not stated, so it's useless...
            has_signature=False,
        )
