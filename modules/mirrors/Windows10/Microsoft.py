from modules.mirrors.GenericComplexMirror import GenericComplexMirror
from modules.SumType import SumType
from modules.WindowsConsumerDownload import WindowsConsumerDownloader


class Microsoft(GenericComplexMirror):
    def __init__(self, lang: str) -> None:
        super().__init__(
            url="https://www.microsoft.com/en-us/software-download/windows10ISO",
            version_regex=r"Version (.+)<",
            version_separator="H",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "deflate, gzip",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
            },
        )
        self.lang = lang

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        hash = WindowsConsumerDownloader.windows_consumer_file_hash("10", self.lang)
        return (
            [SumType.SHA256],
            [hash],
        )

    def _get_download_link(self) -> str:
        return WindowsConsumerDownloader.windows_consumer_download("10", self.lang)
