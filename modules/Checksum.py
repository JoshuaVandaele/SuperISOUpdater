import hashlib
import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path


class SumType(Enum):
    BLAKE3 = ("blake3", "b3sum")
    BLAKE2b = ("blake2b", "blake2", "b2sum")
    SHA512 = ("sha512",)
    SHA256 = ("sha256",)
    SHA1 = ("sha1",)
    MD5 = ("md5",)

    def matches(self, string: str) -> bool:
        return any(v in string.lower() for v in self.value)

    @classmethod
    def _missing_(cls, value: object) -> "SumType | None":
        if isinstance(value, str):
            for member in cls:
                if member.matches(value):
                    return member
        return None


class Checksum(ABC):
    READ_CHUNK_SIZE = 524_288  # 512KiB

    def __init__(self, value: str) -> None:
        self.value = value.lower()

    @staticmethod
    def from_sum_type(sum_type: SumType, value: str) -> Checksum:
        match (sum_type):
            case SumType.MD5:
                return MD5Sum(value)
            case SumType.SHA1:
                return SHA1Sum(value)
            case SumType.SHA256:
                return SHA256Sum(value)
            case SumType.SHA512:
                return SHA512Sum(value)
            case SumType.BLAKE2b:
                return BLAKE2bSum(value)
            case SumType.BLAKE3:
                return BLAKE3Sum(value)

    @classmethod
    @abstractmethod
    def compute_file_hash(cls, file: Path) -> str | None:
        """Computes the hash of a given file.

        Args:
            file (Path): Path to the file to hash.

        Returns:
            str | None: The hex digest, or None if the algorithm is not supported.
        """
        raise NotImplementedError()

    def verify_file(self, file: Path) -> bool:
        digest = self.compute_file_hash(file)

        if digest is None:
            logging.info(
                f"[{type(self).__name__}] No hash implementation, skipping verification"
            )
            return True

        logging.debug(f"[{type(self).__name__}] {file.resolve()} -> {digest}")
        return self.value == digest


class HashlibSum(Checksum):
    SUM_TYPE: SumType

    @classmethod
    def compute_file_hash(cls, file: Path) -> str:
        with open(file, "rb") as f:
            file_hash = hashlib.new(cls.SUM_TYPE.value[0])
            while chunk := f.read(Checksum.READ_CHUNK_SIZE):
                file_hash.update(chunk)
        return file_hash.hexdigest()


class MD5Sum(HashlibSum):
    SUM_TYPE = SumType.MD5


class SHA1Sum(HashlibSum):
    SUM_TYPE = SumType.SHA1


class SHA256Sum(HashlibSum):
    SUM_TYPE = SumType.SHA256


class SHA512Sum(HashlibSum):
    SUM_TYPE = SumType.SHA512


class BLAKE2bSum(HashlibSum):
    SUM_TYPE = SumType.BLAKE2b


class BLAKE3Sum(Checksum):
    @classmethod
    def compute_file_hash(cls, file: Path) -> None:
        return None
