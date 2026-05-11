from modules.ISOPath import ISOPath
from modules.mirrors.UbuntuFlavor.UbuntuFlavorMirrorManager import (
    UbuntuFlavorMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class Lubuntu(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = UbuntuFlavorMirrorManager("lubuntu", arch, edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=["amd64"],
            valid_editions=["desktop"],
        )
