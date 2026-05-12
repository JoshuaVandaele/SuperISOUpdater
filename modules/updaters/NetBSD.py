from modules.ISOPath import ISOPath
from modules.mirrors.NetBSD.NetBSDMirrorManager import NetBSDMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class NetBSD(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str | None = None,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = NetBSDMirrorManager(arch)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=[
                "amd64",
                "evbarm-aarch64",
                "evbarm-aarch64eb",
                "evbmips-mips64eb",
                "evbmips-mips64el",
                "evbmips-mipseb",
                "evbmips-mipsel",
                "evbmips-mipsn64eb",
                "evbmips-mipsn64el",
                "evbppc",
                "hpcarm",
                "i386",
                "sparc64",
            ],
        )
