from modules.ISOPath import ISOPath
from modules.mirrors.MemTest86Plus.MemTest86PlusMirrorManager import (
    MemTest86PlusMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class MemTest86Plus(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str | None = None,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = MemTest86PlusMirrorManager(arch)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=["x86_64", "i586"],
        )
