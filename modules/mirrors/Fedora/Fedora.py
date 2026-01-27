import re

import requests_cache

from modules.mirrors.GenericMirror import GenericMirror
from modules.SumType import SumType
from modules.utils import parse_hash
from modules.Version import Version


class Fedora(GenericMirror):
    def __init__(self, arch: str, edition: str, spin: bool) -> None:
        self.spin = spin
        self.session = requests_cache.CachedSession(backend="memory")
        version = self.determine_version()
        if self.spin:
            url = f"https://download.fedoraproject.org/pub/fedora/linux/releases/{version}/Spins/{arch}/iso/"
        else:
            url = f"https://download.fedoraproject.org/pub/fedora/linux/releases/{version}/{edition}/{arch}/iso/"
        super().__init__(
            url=url,
            file_regex=rf"Fedora-{edition}.+{arch}.+iso",
            version=version,
            version_separator="",
            # TODO: The CHECKSUM file is signed and should be verified
            has_signature=False,
        )

    def determine_version(self) -> Version:
        r = self.session.get(
            "https://download.fedoraproject.org/pub/fedora/linux/releases/"
        )
        r.raise_for_status()

        versions = re.findall(r'href="(\d+)/"', r.text)
        if not versions:
            raise ValueError(f"No version found on the page '{r.url}'")

        latest_version = max(map(int, versions))

        return Version(f"{latest_version}", "")

    def _determine_sums(self):
        if self.spin:
            return [], []
        checksum_urls = [url for url in self._urls() if re.search(r".+CHECKSUM", url)]
        if len(checksum_urls) != 1:
            raise ValueError(f"Found {len(checksum_urls)} checksum files, expected 1.")

        sum_file = self.session.get(checksum_urls[0], headers=self.headers)
        sum_file.raise_for_status()

        sum_file_text = sum_file.text.strip()

        hash_sum_type: SumType | None = None
        for sum_type in SumType:
            if not re.search(rf"Hash: {sum_type.value}".lower(), sum_file_text.lower()):
                continue
            if hash_sum_type:
                raise ValueError(
                    f"Found two hash types: {hash_sum_type} and {sum_type.value}. Can only have one."
                )
            hash_sum_type = sum_type
        if not hash_sum_type:
            raise ValueError("Could not find the type of hash used.")

        hash = parse_hash(sum_file_text, rf"\({self._file_regex}\)", -1)
        return [hash_sum_type], [hash]
