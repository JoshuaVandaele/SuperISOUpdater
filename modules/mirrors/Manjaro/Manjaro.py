from modules.Checksum import SHA256Sum
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import parse_hash


class Manjaro(GenericHTTPMirror):
    def __init__(self, edition: str) -> None:
        super().__init__(
            uri="https://manjaro.org/products/download/x86",
            file_regex=rf"manjaro-{edition}-([\d\.]+)-\d+-linux\d+\.iso",
            version_regex=rf"manjaro-{edition}-([\d\.]+)-\d+-linux\d+\.iso",
        )

    def _determine_public_key(self):
        # https://wiki.manjaro.org/index.php/How-to_verify_GPG_key_of_official_.ISO_images
        r = self.session.get(
            "https://gitlab.manjaro.org/packages/core/manjaro-keyring/-/raw/master/manjaro.gpg"
        )
        r.raise_for_status()
        return r.content

    def _determine_signature(self):
        r = self.session.get(f"{self.download_link}.sig")
        r.raise_for_status()
        return r.content

    def _determine_sums(self):
        r = self.session.get(f"{self.download_link}.sha256")
        r.raise_for_status()
        return [SHA256Sum(parse_hash(r.text, self._file_regex, 0))]
