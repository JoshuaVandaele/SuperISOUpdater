from pathlib import Path

from modules.mirrors.Windows11.Windows11MirrorManager import Windows11MirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Windows11(GenericUpdater):
    """
    A class representing an updater for Windows 11.

    Attributes:
        download_page (requests.Response): The HTTP response containing the download page HTML.
        soup_download_page (BeautifulSoup): The parsed HTML content of the download page.

    Note:
        This class inherits from the abstract base class GenericUpdater.
    """

    def __init__(self, folder_path: Path, lang: str, file_name: str) -> None:
        self.valid_langs = [
            "Arabic",
            "Brazilian Portuguese",
            "Bulgarian",
            "Chinese",
            "Chinese",
            "Croatian",
            "Czech",
            "Danish",
            "Dutch",
            "English",
            "English International",
            "Estonian",
            "Finnish",
            "French",
            "French Canadian",
            "German",
            "Greek",
            "Hebrew",
            "Hungarian",
            "Italian",
            "Japanese",
            "Korean",
            "Latvian",
            "Lithuanian",
            "Norwegian",
            "Polish",
            "Portuguese",
            "Romanian",
            "Russian",
            "Serbian Latin",
            "Slovak",
            "Slovenian",
            "Spanish",
            "Spanish (Mexico)",
            "Swedish",
            "Thai",
            "Turkish",
            "Ukrainian",
        ]
        self.lang = lang
        mirror_mgr = Windows11MirrorManager(lang)
        super().__init__(folder_path / file_name, mirror_mgr)
