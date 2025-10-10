from modules.mirrors.GenericMirror import GenericMirror


class TrueNAS(GenericMirror):
    def __init__(self) -> None:
        super().__init__(
            url="https://www.truenas.com/download-truenas-community-edition",
            file_regex=r"TrueNAS-SCALE-.+\.iso",
            version_regex=r"TrueNAS-SCALE-([\d\.]+)\.iso",
        )

    def _get_public_key(self) -> bytes | None:
        r = self.session.get("https://security.truenas.com/secteam.pgp")
        r.raise_for_status()
        return r.content
