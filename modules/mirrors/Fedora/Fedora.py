import re

import requests_cache

from modules.Checksum import Checksum, SumType
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import pgp_check_message
from modules.Version import Version


class Fedora(GenericHTTPMirror):
    def __init__(self, arch: str, edition: str, spin: bool) -> None:
        self.spin = spin
        self.session = requests_cache.CachedSession(backend="memory")
        version = self.determine_version()
        if self.spin:
            url = f"https://download.fedoraproject.org/pub/fedora/linux/releases/{version}/Spins/{arch}/iso/"
        else:
            url = f"https://download.fedoraproject.org/pub/fedora/linux/releases/{version}/{edition}/{arch}/iso/"
        added_regex: str = ""
        # TODO: This should be user-configurable in a clean way...
        # Maybe Server/netinst and Server/dvd?
        if edition == "Server":
            added_regex = r"netinst"
        super().__init__(
            uri=url,
            file_regex=rf"Fedora-{edition}(.+)?{added_regex}(.+)?{arch}(.+)?\.iso",
            version=version,
            version_separator="",
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

    def __get_checksum_file(self):
        checksum_urls = [url for url in self._urls() if "CHECKSUM" in url]
        if len(checksum_urls) != 1:
            raise ValueError(f"Found {len(checksum_urls)} checksum files, expected 1.")

        sum_file = self.session.get(checksum_urls[0], headers=self.headers)
        sum_file.raise_for_status()
        return sum_file

    def _determine_sums(self) -> list[Checksum]:
        sums: list[Checksum] = []
        if self.spin:
            return sums
        sum_file = self.__get_checksum_file()
        sum_file_text = sum_file.text.strip()
        for line in sum_file_text.splitlines():
            if not re.search(self._file_regex, line):
                continue
            for sum_type in SumType:
                if not sum_type.matches(line):
                    continue
                sums.append(Checksum.from_sum_type(sum_type, line.split()[-1]))
                break
        return sums

    def _determine_public_key(self) -> bytes:
        # https://fedoraproject.org/security/
        r = self.session.get("https://fedoraproject.org/fedora.gpg")
        r.raise_for_status()
        return r.content

    def _determine_signature(self) -> bytes:
        return self.__get_checksum_file().content

    def signature_check(self, _) -> bool:
        return pgp_check_message(self.signature, self.public_key)
