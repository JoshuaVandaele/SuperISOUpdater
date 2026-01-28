from enum import StrEnum


class SumType(StrEnum):
    BLAKE3 = "blake3"
    BLAKE2b = "blake2b"
    SHA512 = "sha512"
    SHA256 = "sha256"
    SHA1 = "sha1"
    MD5 = "md5"
