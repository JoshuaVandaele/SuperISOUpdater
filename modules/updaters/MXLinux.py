from modules.ISOPath import ISOPath
from modules.mirrors.MXLinux.MXLinuxMirrorManager import MXLinuxMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class MXLinux(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = MXLinuxMirrorManager(arch, edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=[
                "x64",
            ],
            valid_editions=[
                "Xfce",
                "Xfce_ahs",
                "KDE",
                "Fluxbox",
            ],
        )
