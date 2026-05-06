from modules.ISOPath import ISOPath
from modules.mirrors.Tails.TailsMirrorManager import TailsMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Tails(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str | None = None,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = TailsMirrorManager(arch)
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
