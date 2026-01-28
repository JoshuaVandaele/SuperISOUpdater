import shutil
from pathlib import Path

from modules.exceptions import IntegrityCheckError
from modules.mirrors.GenericMirror import GenericMirror
from modules.utils import extract_matching_file


class Memtest(GenericMirror):
    def __init__(self, arch: str) -> None:
        super().__init__(
            url="https://www.memtest.org/",
            file_regex=rf"mt86plus_(.+)_{arch}.iso\.zip",
            version_regex=rf"mt86plus_(.+)_{arch}\.iso\.zip",
            has_signature=False,
        )

    def download_and_verify(self, file: Path) -> bool:
        if not super().download_and_verify(file):
            return False
        try:
            with extract_matching_file(file, r"\.iso$") as extracted:
                extracted: Path
                shutil.move(extracted, file)
        except Exception as e:
            raise IntegrityCheckError(f"Failed to extract {file}") from e
        return True
