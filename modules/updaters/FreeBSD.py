from modules.ISOPath import ISOPath
from modules.mirrors.FreeBSD.FreeBSDMirrorManager import FreeBSDMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class FreeBSD(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = FreeBSDMirrorManager(arch, edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=[
                "amd64",
                "aarch64",
                "powerpc64",
                "powerpc64le",
                "riscv64",
            ],
            valid_editions=["bootonly", "dvd1", "disc1"],
        )
