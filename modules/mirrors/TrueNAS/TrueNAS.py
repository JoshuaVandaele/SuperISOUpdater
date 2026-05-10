from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror


class TrueNAS(GenericHTTPMirror):
    def __init__(self) -> None:
        super().__init__(
            uri="https://www.truenas.com/download",
            download_regex=r"TrueNAS-SCALE-.+\.iso",
            version_regex=r"TrueNAS-SCALE-([\d\.]+)\.iso",
        )

    def _determine_public_key(self) -> bytes | None:
        r = self.session.get("https://security.truenas.com/secteam.pgp")
        r.raise_for_status()
        return r.content
