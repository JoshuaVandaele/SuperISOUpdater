from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Self

from modules.Checksum import Checksum
from modules.exceptions import IntegrityCheckError
from modules.utils import pgp_check
from modules.Version import Version


class GenericMirror(ABC):
    """
    An abstract class representing a generic mirror for downloading files.
    Subclasses must:
    - Find the latest version available from the mirror
    - Get and verify the checksums available
    - Determine the speed from the user to the mirror
    - Get and verify the PGP/GPG signature if available
    """

    _init_steps: list[str] = [
        "_init_version",
        "_init_checksums",
        "_init_signature",
        "_init_speed",
    ]

    def __init__(
        self,
        uri: str,
        version_class: type[Version] = Version,
        version_separator: str = ".",
        version_padding: int = 0,
        has_signature: bool = True,
        signed_file: Path | Callable[[Self], Path] | None = None,
    ) -> None:
        """
        Args:
            uri (str): The URI of the mirror page.
            version_class (type[Version], optional): Class or subclass of Version to use. Defaults to Version.
            version_separator (str): The separator used to join the components. Defaults to '.'.
            version_padding (int): The number of digits to zero-pad each component. Defaults to 0.
            has_signature (bool, optional): Should we check for a cryptographic signature. Defaults to True.
            signed_file (Path, optional): Which file to check the signature against? Defaults to the downloaded file.
        """
        self.__uri = uri
        self.__version_class = version_class
        self.__version_separator = version_separator
        self.__version_padding = version_padding
        self.__has_signature = has_signature
        self.__signed_file = signed_file

    @property
    def uri(self):
        return self.__uri

    @property
    def VersionClass(self):
        return self.__version_class

    @property
    def version_separator(self):
        return self.__version_separator

    @property
    def version_padding(self):
        return self.__version_padding

    @property
    def has_signature(self):
        return self.__has_signature

    @property
    def signed_file(self):
        return (
            self.__signed_file
            if not callable(self.__signed_file)
            else self.__signed_file(self)
        )

    def initialize(self) -> None:
        for step in self._init_steps:
            getattr(self, step)()

    def checksum_file(self, file: Path) -> bool:
        for checksum in self.checksums:
            if not checksum.verify_file(file):
                return False
        return True

    def signature_check(self, file: Path) -> bool:
        return pgp_check(file, signature=self.signature, public_key=self.public_key)

    def download_and_verify(self, file: Path) -> None:
        """Downloads a file and verifies its integrity through checksum and signature.

        Args:
            file (Path): Download location

        Raises:
            IntegrityCheckError: If a verification fails
        """
        self._download_file(file)

        if not self.checksum_file(file):
            if file:
                file.unlink()
            raise IntegrityCheckError("Integrity check failed! (Checksum)")

        if not self.has_signature:
            return

        sig_error: str | None = None
        signature_success: bool
        try:
            signature_success = self.signature_check(self.signed_file or file)
        except Exception as e:
            signature_success = False
            sig_error = str(e)

        if not signature_success:
            if file:
                file.unlink()
            raise IntegrityCheckError(
                f"Integrity check failed! (Signature){f': {sig_error}' if sig_error else ''}"
            )

    def _init_version(self) -> None:
        self.version = self._determine_latest_version()

    def _init_checksums(self) -> None:
        self.checksums = self._determine_sums()

    def _init_signature(self) -> None:
        if not self.has_signature:
            return
        self.public_key = self._determine_public_key()
        self.signature = self._determine_signature()

    def _init_speed(self) -> None:
        self.speed = self._determine_speed()

    @abstractmethod
    def _determine_latest_version(self) -> Version:
        raise NotImplementedError()

    @abstractmethod
    def _determine_sums(self) -> list[Checksum]:
        raise NotImplementedError()

    @abstractmethod
    def _determine_public_key(self) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def _determine_signature(self) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def _determine_speed(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def _download_file(self, file: Path):
        raise NotImplementedError()
