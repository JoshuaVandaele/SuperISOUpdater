import shutil
from pathlib import Path

from modules.exceptions import IntegrityCheckError
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import extract_matching_zip_file


class Memtest(GenericHTTPMirror):
    def __init__(self, arch: str) -> None:
        super().__init__(
            uri="https://www.memtest.org/",
            file_regex=rf"mt86plus_(.+)_{arch}.iso\.zip",
            version_regex=rf"mt86plus_(.+)_{arch}\.iso\.zip",
            has_signature=False,
        )

    def download_and_verify(self, file: Path):
        zip_file = Path(f"{file}.zip")
        super().download_and_verify(zip_file)
        try:
            with extract_matching_zip_file(zip_file, r"\.iso$") as extracted:
                extracted: Path
                shutil.move(extracted, file)
        except Exception as e:
            raise IntegrityCheckError(f"Failed to extract {zip_file}") from e
        finally:
            zip_file.unlink(missing_ok=True)
