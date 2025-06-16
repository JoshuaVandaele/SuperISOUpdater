from pathlib import Path

from modules.exceptions import NoMirrorsError
from modules.mirrors.UltimateBootCD.UltimateBootCDMirrorManager import (
    UltimateBootCDMirrorManager,
)
from modules.updaters.GenericUpdater import GenericUpdater
from modules.Version import Version

FILE_NAME = "ubcd[[VER]].iso"


class UltimateBootCD(GenericUpdater):
    """
    A class representing an updater for Ultimate Boot CD.

    Attributes:
        soup_mirrors (list[tuple[SumType, BeautifulSoup]])
        download_table (Tag)

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path) -> None:
        file_path = folder_path / FILE_NAME
        super().__init__(file_path)

        self.mirror_mgr = UltimateBootCDMirrorManager()

    def install_latest_version(self) -> None:
        old_file = self._get_local_file()
        new_file = self._get_complete_normalized_file_path(absolute=True)

        if old_file:
            old_file.with_suffix(".old").replace(old_file)

        try:
            self.mirror_mgr.attempt_download(new_file)
        except NoMirrorsError as e:
            if old_file:
                old_file.replace(new_file)
            new_file.unlink(missing_ok=True)
            raise RuntimeError from e

        if old_file:
            old_file.unlink()

    def _get_latest_version(self) -> Version:
        return self.mirror_mgr.current_mirror.version
