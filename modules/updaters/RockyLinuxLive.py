from modules.ISOPath import ISOPath
from modules.mirrors.RockyLinuxLive.RockyLinuxLiveMirrorManager import (
    RockyLinuxLiveMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class RockyLinuxLive(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = RockyLinuxLiveMirrorManager(arch, edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=["x86_64", "aarch64"],
            valid_editions=["KDE", "Workstation", "Workstation-Lite"],
        )
