from modules.ISOPath import ISOPath
from modules.mirrors.ArtixLinux.ArtixLinuxMirrorManager import ArtixLinuxMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class ArtixLinux(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = ArtixLinuxMirrorManager(arch=arch, edition=edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=[
                "x86_64",
            ],
            valid_editions=[
                "base-dinit",
                "base-openrc",
                "base-runit",
                "base-s6",
                "cinnamon-dinit",
                "cinnamon-openrc",
                "cinnamon-runit",
                "cinnamon-s6",
                "lxde-dinit",
                "lxde-openrc",
                "lxde-runit",
                "lxde-s6",
                "lxqt-dinit",
                "lxqt-openrc",
                "lxqt-runit",
                "lxqt-s6",
                "mate-dinit",
                "mate-openrc",
                "mate-runit",
                "mate-s6",
                "plasma-dinit",
                "plasma-openrc",
                "plasma-runit",
                "plasma-s6",
                "xfce-dinit",
                "xfce-openrc",
                "xfce-runit",
                "xfce-s6",
            ],
        )
