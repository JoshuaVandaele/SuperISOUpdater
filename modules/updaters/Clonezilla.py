from modules.ISOPath import ISOPath
from modules.mirrors.Clonezilla.ClonezillaMirrorManager import ClonezillaMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Clonezilla(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str | None = None,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = ClonezillaMirrorManager(arch)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=[
                "amd64",
            ],
        )
