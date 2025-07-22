from modules.mirrors.GenericMirror import GenericMirror


class Rackspace(GenericMirror):
    def __init__(self) -> None:
        super().__init__(
            url="https://mirror.rackspace.com/archlinux/iso/latest/",
            file_regex=r"archlinux-.+-x86_64\.iso",
            version_regex=r"archlinux-(.+)-x86_64\.iso",
            version_padding=2,
        )
