from modules.ISOPath import ISOPath
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

    def __init__(
        self,
        iso_path: ISOPath,
        edition: str,
        arch: str | None = None,
        lang: str | None = None,
    ) -> None:
        if edition.lower() == "diskette":
            extension = "img"
        else:
            extension = "iso"

        mirror_mgr = HDAT2MirrorManager(edition, extension)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            extension=extension,
            valid_editions=["full", "lite", "diskette"],
        )
