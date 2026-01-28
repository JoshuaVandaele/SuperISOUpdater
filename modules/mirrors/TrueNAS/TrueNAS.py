from modules.mirrors.GenericMirror import GenericMirror


class TrueNAS(GenericMirror):
    def __init__(self) -> None:
        super().__init__(
            url="https://www.truenas.com/download",
            file_regex=r"TrueNAS-SCALE-.+\.iso",
            version_regex=r"TrueNAS-SCALE-([\d\.]+)\.iso",
            headers={
                "User-Agent": "Mozilla.5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            },
        )

    def _get_public_key(self) -> bytes | None:
        r = self.session.get("https://security.truenas.com/secteam.pgp")
        r.raise_for_status()
        return r.content
