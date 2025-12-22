from pathlib import Path

from modules.mirrors.Windows10.Windows10MirrorManager import Windows10MirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Windows10(GenericUpdater):
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
        mirror_mgr = Windows10MirrorManager(lang)
        super().__init__(folder_path / file_name, mirror_mgr)
