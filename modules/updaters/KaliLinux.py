from modules.ISOPath import ISOPath
from modules.mirrors.KaliLinux.KaliLinuxMirrorManager import KaliLinuxMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class KaliLinux(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        edition: str,
        arch: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = KaliLinuxMirrorManager(arch, edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=["amd64", "arm64"],
            valid_editions=[
                "installer",
                "installer-everything",
                "installer-netinst",
                "installer-purple",
                "live",
            ],
        )
