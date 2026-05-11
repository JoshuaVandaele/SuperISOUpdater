from modules.ISOPath import ISOPath
from modules.mirrors.EndeavourOS.EndeavourOSMirrorManager import (
    EndeavourOSMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class EndeavourOS(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str | None = None,
        edition: str | None = None,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = EndeavourOSMirrorManager()
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
        )
