from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror


class OVH(GenericHTTPMirror):
    def __init__(self, arch: str, edition: str) -> None:
        super().__init__(
            uri=f"https://alpinelinux.mirrors.ovh.net/latest-stable/releases/{arch}/",
            file_regex=rf"alpine-{edition}-(.+?)-{arch}.iso",
            version_regex=rf"alpine-{edition}-(.+?)-{arch}.iso",
        )

    def _determine_public_key(self) -> bytes | None:
        r = self.session.get("https://alpinelinux.org/keys/ncopa.asc")
        r.raise_for_status()
        return r.content
