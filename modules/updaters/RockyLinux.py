from modules.ISOPath import ISOPath
from modules.updaters.GenericUpdater import GenericUpdater


class RockyLinux(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str | None = None,
        edition: str | None = None,
        lang: str | None = None,
    ) -> None:
        raise NotImplementedError()
