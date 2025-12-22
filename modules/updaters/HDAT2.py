from pathlib import Path

from modules.mirrors.HDAT2.HDAT2MirrorManager import HDAT2MirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class HDAT2(GenericUpdater):
    """
    A class representing an updater for HDAT2.

    Attributes:
        valid_editions (list[str]): List of valid editions to use
        edition (str): Edition to download
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, edition: str, file_name: str) -> None:
        self.valid_editions = ["full", "lite", "diskette"]
        self.edition = edition.lower()

        if self.edition == "diskette":
            extension = "img"
        else:
            extension = "iso"

        self.file_name = file_name.replace("[[EXT]]", extension)

        mirror_mgr = HDAT2MirrorManager(self.edition, extension)
        super().__init__(folder_path / self.file_name, mirror_mgr)
