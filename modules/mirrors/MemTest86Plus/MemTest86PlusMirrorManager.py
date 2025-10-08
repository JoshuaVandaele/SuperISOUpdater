from pathlib import Path

from modules.exceptions import IntegrityCheckError
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.mirrors.MemTest86Plus.Memtest import Memtest
from modules.utils import extract_matching_file


class MemTest86PlusMirrorManager(GenericMirrorManager):
    def __init__(
        self,
    ) -> None:
        mirrors = [Memtest()]
        super().__init__(mirrors)

    def _download_and_checksum(mirror, file) -> bool:
        if not super()._download_and_checksum(mirror, file):
            return False

        try:
            with extract_matching_file(file, r"\\.iso$") as extracted:
                extracted: Path
                extracted.rename(file)
        except Exception as e:
            raise IntegrityCheckError(f"Failed to extract {file}") from e
        return True
