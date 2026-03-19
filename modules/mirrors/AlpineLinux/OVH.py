from modules.mirrors.GenericMirror import GenericMirror


class OVH(GenericMirror):
    def __init__(self, arch: str, edition: str) -> None:
        super().__init__(
            url=f"https://alpinelinux.mirrors.ovh.net/latest-stable/releases/{arch}/",
            file_regex=rf"alpine-{edition}-(.+?)-{arch}.iso",
            version_regex=rf"alpine-{edition}-(.+?)-{arch}.iso",
        )

    def _get_public_key(self) -> bytes | None:
        r = self.session.get("https://alpinelinux.org/keys/ncopa.asc")
        r.raise_for_status()
        return r.content
