from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType
from modules.utils import parse_hash


class Manjaro(GenericMirror):
    def __init__(self, edition: str) -> None:
        super().__init__(
            url="https://manjaro.org/products/download/x86",
            file_regex=rf"manjaro-{edition}-([\d\.]+)-\d+-linux\d+\.iso",
            version_regex=rf"manjaro-{edition}-([\d\.]+)-\d+-linux\d+\.iso",
        )

    def _get_public_key(self):
        # https://wiki.manjaro.org/index.php/How-to_verify_GPG_key_of_official_.ISO_images
        r = self.session.get(
            "https://gitlab.manjaro.org/packages/core/manjaro-keyring/-/raw/master/manjaro.gpg"
        )
        r.raise_for_status()
        return r.content

    def _get_signature(self):
        r = self.session.get(f"{self.download_link}.sig")
        r.raise_for_status()
        return r.content

    def _determine_sums(self):
        r = self.session.get(f"{self.download_link}.sha256")
        r.raise_for_status()
        return [SumType.SHA256], [parse_hash(r.text, self._file_regex, 0)]
