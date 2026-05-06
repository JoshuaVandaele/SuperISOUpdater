from modules.ISOPath import ISOPath
from modules.mirrors.Rescuezilla.RescuezillaMirrorManager import (
    RescuezillaMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class Rescuezilla(GenericUpdater):

    def __init__(
        self,
        iso_path: ISOPath,
        edition: str,
        arch: str | None = None,
        lang: str | None = None,
    ) -> None:
        arch = "32bit" if edition.lower() == "bionic" else "64bit"
        mirror_mgr = RescuezillaMirrorManager(edition=edition, arch=arch)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=["64bit", "32bit"],
            valid_editions=["bionic", "focal", "jammy", "noble"],
        )
