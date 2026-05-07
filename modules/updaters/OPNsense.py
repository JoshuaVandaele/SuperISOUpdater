from modules.ISOPath import ISOPath
from modules.mirrors.OPNsense.OPNsenseMirrorManager import OPNsenseMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class OPNsense(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        mirror_mgr = OPNsenseMirrorManager(arch, edition)
        extension = "iso" if edition.lower() == "dvd" else "img"
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            extension=extension,
            valid_archs=["amd64"],
            valid_editions=["dvd", "nano", "serial", "vga"],
        )
