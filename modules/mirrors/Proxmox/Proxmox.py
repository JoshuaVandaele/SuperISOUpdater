import re

from bs4 import BeautifulSoup
from datetime import datetime
from modules.Checksum import SHA256Sum
from modules.DotDashVersion import DotDashVersion
from modules.mirrors.GenericHTTPMirror import GenericHTTPMirror
from modules.utils import parse_hash


class Proxmox(GenericHTTPMirror):
    def __init__(self, edition: str) -> None:
        super().__init__(
            uri="https://enterprise.proxmox.com/iso/",
            download_regex=rf"proxmox-{edition}_(.+)\.iso",
            version_regex=rf"proxmox-{edition}_(.+)\.iso",
            version_class=DotDashVersion,
        )

    def _determine_public_key(self) -> bytes:
        # https://enterprise.proxmox.com/iso/#verify indicates use of a single `release` key, but the actual signatures use multiple, so verification fails. Instead, use the `archive-keyring`.
        key_index_url = "https://enterprise.proxmox.com/debian/"
        key_line_regex = r"(?P<filename>.+\.gpg)\s{2,}(?P<modified>\d{2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4} \d{2}:\d{2})\s{2,}(?P<size>\d+)"

        idx_r = self.session.get(key_index_url, headers=self.headers)
        idx_r.raise_for_status()
        idx_soup = BeautifulSoup(idx_r.content, features="html.parser")

        pre_tag = idx_soup.find("pre")
        if not pre_tag:
            raise ValueError(
                f"Invalid file listing on {key_index_url} - cannot retrieve Proxmox public key for signature verification!"
            )

        pre_lines = pre_tag.get_text().strip().splitlines()
        key_lines = sorted(
            [
                re.match(key_line_regex, key_line)
                for key_line in pre_lines
                if "archive-keyring" in key_line
            ],
            key=lambda x: datetime.strptime(x["modified"], "%d-%b-%Y %H:%M"),
            reverse=True,
        )

        key_r = self.session.get(f"{key_index_url}{key_lines[0]['filename']}")
        key_r.raise_for_status()
        return key_r.content

    def _determine_signature(self) -> bytes | None:
        r = self.session.get(f"{self.download_link}.asc")
        r.raise_for_status()
        return r.content

    def _determine_sums(self):
        r = self.session.get(f"{self.download_link}.sha256")
        r.raise_for_status()
        return [SHA256Sum(parse_hash(r.text, self._download_regex, 0))]
