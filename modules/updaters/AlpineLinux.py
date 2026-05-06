from modules.ISOPath import ISOPath
from modules.mirrors.AlpineLinux.AlpineLinuxMirrorManager import (
    AlpineLinuxMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater


class AlpineLinux(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = AlpineLinuxMirrorManager(arch, edition)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=[
                "aarch64",
                "armv7",
                "loongarch64",
                "ppc64le",
                "riscv64",
                "s390x",
                "x86",
                "x86_64",
            ],
            valid_editions=["standard"],
        )
