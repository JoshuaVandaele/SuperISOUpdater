from pathlib import Path

from modules.mirrors.Fedora.FedoraMirrorManager import FedoraMirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Fedora(GenericUpdater):
    def __init__(
        self, folder_path: Path, arch: str, edition: str, file_name: str
    ) -> None:
        self.valid_archs = ["aarch64", "x86_64"]
        self.valid_editions = [
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
        ]
        spin = "Spins/" in edition
        if spin:
            edition = edition[6:]
        self.edition = edition
        self.arch = arch
        mirror_mgr = FedoraMirrorManager(arch, edition, spin)
        super().__init__(folder_path / file_name, mirror_mgr)
