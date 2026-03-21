from pathlib import Path

from modules.updaters.GenericUpdater import GenericUpdater


class RockyLinux(GenericUpdater):
    def __init__(self, folder_path: Path, file_name: str, edition: str) -> None:
        raise NotImplementedError()
