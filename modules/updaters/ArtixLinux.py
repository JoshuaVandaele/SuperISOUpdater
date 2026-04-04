from pathlib import Path

from modules.mirrors.ArtixLinux.ArtixLinuxMirrorManager import ArtixLinuxMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class ArtixLinux(GenericUpdater):
    def __init__(
        self, folder_path: Path, arch: str, edition: str, file_name: str
    ) -> None:
        self.valid_archs = [
            "x86_64",
        ]
        self.arch = arch
        self.valid_editions = [
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
        ]
        self.edition = edition
        mirror_mgr = ArtixLinuxMirrorManager(arch=arch, edition=edition)
        super().__init__(folder_path / file_name, mirror_mgr)
