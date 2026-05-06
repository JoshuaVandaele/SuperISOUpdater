from modules.ISOPath import ISOPath
from modules.mirrors.Debian.DebianMirrorManager import DebianMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Debian(GenericUpdater):

    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str | None = None,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = DebianMirrorManager(arch)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=[
                "amd64",
                "arm64",
                "armhf",
                "ppc64el",
                "riscv64",
                "s390x",
            ],
        )
