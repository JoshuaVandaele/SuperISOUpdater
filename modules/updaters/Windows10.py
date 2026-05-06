from modules.ISOPath import ISOPath
from modules.mirrors.Windows10.Windows10MirrorManager import Windows10MirrorManager
from modules.updaters.GenericUpdater import GenericUpdater


class Windows10(GenericUpdater):

    def __init__(
        self,
        iso_path: ISOPath,
        lang: str,
        arch: str | None = None,
        edition: str | None = None,
    ) -> None:
        mirror_mgr = Windows10MirrorManager(lang)
        super().__init__(
            iso_path=iso_path,
            mirror_mgr=mirror_mgr,
            arch=arch,
            edition=edition,
            lang=lang,
            valid_langs=[
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
            ],
        )
