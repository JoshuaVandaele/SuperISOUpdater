from modules.ISOPath import ISOPath
from modules.mirrors.CachyOS.CachyOSMirrorManager import CachyOSMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class CachyOS(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        edition: str,
        arch: str | None = None,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = CachyOSMirrorManager(edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_editions=["desktop", "handheld"],
        )
