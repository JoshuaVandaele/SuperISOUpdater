from modules.ISOPath import ISOPath
from modules.mirrors.Fedora.FedoraMirrorManager import FedoraMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Fedora(GenericUpdater):
    def __init__(
        self,
        iso_path: ISOPath,
        arch: str,
        edition: str,
        lang: str | None = None,
    ) -> None:
        spin = "Spins/" in edition
        if spin:
            edition = edition[6:]
        mirror_mgr = FedoraMirrorManager(arch, edition, spin)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_archs=["aarch64", "x86_64"],
            valid_editions=[
                "Everything",
                "KDE",
                "Kinoite",
                "Server",
                "Silverblue",
                "Workstation",
                "COSMIC",
                "KDE-Mobile",
                "LXQt",
                "MiracleWM",
                "SoaS",
                "Xfce",
                "i3",
            ],
        )
