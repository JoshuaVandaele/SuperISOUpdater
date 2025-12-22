from modules.mirrors.GenericMirror import GenericMirror


class Debian(GenericMirror):
    def __init__(self, arch: str) -> None:
        super().__init__(
            url=f"https://cdimage.debian.org/debian-cd/current/{arch}/iso-cd/",
            file_regex=rf"debian-(\d+(?:\.\d+)+)+-{arch}-netinst.iso",
            version_regex=rf"debian-(\d+(?:\.\d+)+)+-{arch}-netinst.iso",
            has_signature=False,
        )
