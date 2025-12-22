from modules.mirrors.GenericComplexMirror import GenericComplexMirror
from modules.SumType import SumType
from modules.WindowsConsumerDownload import WindowsConsumerDownloader


class Microsoft(GenericComplexMirror):
    def __init__(self, lang: str, arch: str) -> None:
        super().__init__(
            url="https://www.microsoft.com/en-us/software-download/windows11",
            version_regex=r"Version (.+)\)",
            version_separator="H",
            has_signature=False,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "deflate, gzip",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
            },
        )
        self.lang = lang
        self.windows_version = "11" if arch == "x64" else "11arm64"

    def _determine_sums(self) -> tuple[list[SumType], list[str]]:
        hash = WindowsConsumerDownloader.windows_consumer_file_hash(
            self.windows_version, self.lang
        )
        return (
            [SumType.SHA256],
            [hash],
        )

    def _get_download_link(self) -> str:
        return WindowsConsumerDownloader.windows_consumer_download(
            self.windows_version, self.lang
        )
