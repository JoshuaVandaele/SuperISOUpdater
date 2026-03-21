from modules.Checksum import Checksum, SHA256Sum
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.WindowsConsumerDownload import WindowsConsumerDownloader


class Microsoft(GenericHTTPMirror):
    def __init__(self, lang: str) -> None:
        super().__init__(
            uri="https://www.microsoft.com/en-us/software-download/windows10ISO",
            file_regex=rf"Win10_[\dH]+_{lang}_x64v1.iso",
            version_regex=r"Version ([\dH]+)",
            version_separator="H",
            has_signature=False,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "deflate, gzip",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
            },
        )
        self.lang = lang

    def _determine_sums(self) -> list[Checksum]:
        hash = WindowsConsumerDownloader.windows_consumer_file_hash("10", self.lang)
        return [SHA256Sum(hash)]

    def _determine_download_link(self) -> str:
        return WindowsConsumerDownloader.windows_consumer_download("10", self.lang)
