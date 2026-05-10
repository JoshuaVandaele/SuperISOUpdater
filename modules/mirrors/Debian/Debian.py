from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror


class Debian(GenericHTTPMirror):
    def __init__(self, arch: str) -> None:
        super().__init__(
            uri=f"https://cdimage.debian.org/debian-cd/current/{arch}/iso-cd/",
            download_regex=rf"debian-(\d+(?:\.\d+)+)+-{arch}-netinst.iso",
            version_regex=rf"debian-(\d+(?:\.\d+)+)+-{arch}-netinst.iso",
            has_signature=False,
        )
