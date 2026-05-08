from modules.ISOPath import ISOPath
from modules.mirrors.TrueNAS.TrueNASMirrorManager import TrueNASMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class TrueNAS(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str | None = None,
        edition: str | None = None,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = TrueNASMirrorManager()
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
        )
