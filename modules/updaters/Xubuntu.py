from modules.ISOPath import ISOPath
from modules.mirrors.UbuntuFlavor.UbuntuFlavorMirrorManager import (
    UbuntuFlavorMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class Xubuntu(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = UbuntuFlavorMirrorManager("xubuntu", arch, edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=["amd64"],
            valid_editions=["desktop", "minimal"],
        )
