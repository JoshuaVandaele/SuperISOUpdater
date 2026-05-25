import logging
import re
import shutil
import tempfile
import traceback
import zipfile
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import Generator

import gnupg
import requests
import requests_cache
from tqdm import tqdm


def logging_critical_exception(msg, *args, **kwargs):
    """
    Log a critical exception with traceback information.

    Args:
        msg (str): The error message to be logged.
        *args: Variable length argument list to be passed to the logging.critical method.
        **kwargs: Keyword arguments to be passed to the logging.critical method.
    """
    logging.critical(f"{msg}\n{traceback.format_exc()}", *args, **kwargs)


def pgp_check(file_path: Path, signature: str | bytes, public_key: str | bytes) -> bool:
    """Verifies the signature of a file against a public key

    Args:
        file_path (Path): Path to the file to check
        signature (str | bytes): Signature
        public_key (str | bytes): Public Key

    Raises:
        ValueError: If the supplied public key could not be imported.

    Returns:
        bool: Whether the check was successful or not
    """
    try:
        gpg = gnupg.GPG()
    except OSError:
        logging.warning(
            "GnuPG check skipped because GnuPG is not installed. Consider installing it: https://www.gnupg.org/download/#binary"
        )
        return True

    if isinstance(public_key, str):
        public_key = public_key.encode()
    if isinstance(signature, str):
        signature = signature.encode()

    import_result = gpg.import_keys(public_key)
    if not import_result.count:
        raise ValueError("Public key could not be imported.")

    sig_filelike = BytesIO(signature)

    with open(file_path, "rb") as f:
        verify_result = gpg.verify_file(sig_filelike, f.name)

    result = verify_result.valid

    logging.debug(
        f"[pgp_check] {file_path.resolve()}: Signature is{' ' if result else ' not '}valid"
    )

    return result


def pgp_check_message(signed_message: str | bytes, public_key: str | bytes) -> bool:
    """Verifies a PGP signed message
    Args:
        signed_message (str | bytes): The full cleartext signed message, including
                                      the PGP headers, body, and signature block.
        public_key (str | bytes): Public key to verify against.
    Raises:
        ValueError: If the supplied public key could not be imported.
    Returns:
        bool: Whether the signature is valid.
    """
    try:
        gpg = gnupg.GPG()
    except OSError:
        logging.warning(
            "GnuPG check skipped because GnuPG is not installed. "
            "Consider installing it: https://www.gnupg.org/download/#binary"
        )
        return True

    if isinstance(public_key, str):
        public_key = public_key.encode()
    if isinstance(signed_message, str):
        signed_message = signed_message.encode()

    import_result = gpg.import_keys(public_key)
    if not import_result.count:
        raise ValueError("Public key could not be imported.")

    verify_result = gpg.verify(signed_message)
    result = verify_result.valid

    logging.debug(f"[pgp_check_message] Signature is{' ' if result else ' not '}valid")
    return result


def pgp_receive_key(key_id: str, keyserver: str) -> bytes | None:
    """
    Receive a PGP key from a keyserver and import it into the local GPG keyring.

    Args:
        key_id (str): The key ID, fingerprint, or short key of the public key to retrieve.
        keyserver (str): The keyserver to use.

    Returns:
        bytes | None: The key in bytes if successful.
    """
    try:
        gpg = gnupg.GPG()
    except OSError:
        # gpp is not installed
        return None
    logging.debug(f"[pgp_receive_key] Receiving key {key_id} from {keyserver}")
    import_result = gpg.recv_keys(keyserver, key_id)
    if import_result.count > 0:
        key_ascii = gpg.export_keys(key_id)
        if key_ascii:
            logging.debug(f"[pgp_receive_key] Successfully imported key {key_id}")
            return key_ascii.encode("utf-8")

    logging.warning(f"[pgp_receive_key] Key {key_id} could not be found or imported")


def parse_hash(hashes: str, match_regex: str, hash_position_in_line: int):
    """Parse a list of hashes and extract a specific hash based on matching strings.

    Args:
        hashes (str): A string containing a list of hashes.
        match_strings_in_line (list[str]): List of strings that must be present in the line to consider it.
        hash_position_in_line (int): The position of the desired hash in each line.

    Returns:
        The extracted hash value.
    """
    logging.debug(
        f"[parse_hash] Parsing hashes with match strings `{match_regex}` and hash position {hash_position_in_line} in those hashes:\n{hashes}"
    )
    hash = next(
        line.split()[hash_position_in_line]
        for line in hashes.strip().splitlines()
        if re.search(match_regex, line)
    )
    logging.debug(f"[parse_hash] Extracted hash: `{hash}`")
    return hash


def download_file(url: str, local_file: Path, progress_bar: bool = True) -> None:
    """
    Download a file from a given URL and save it to the local file system.

    Args:
        url (str): The URL of the file to download.
        local_file (Path): The path where the downloaded file will be saved on the local file system.
        progress_bar (bool): Whether to show a progress bar during the download (default: True).

    Returns:
        None
    """
    part_file = local_file.with_suffix(".part")
    logging.debug(f"[download_file] Downloading {url} to {part_file.resolve()}")

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))  # Sizes in bytes

            with open(part_file, "wb") as f:
                if progress_bar:
                    with tqdm(
                        total=total_size, unit="B", desc=part_file.name, unit_scale=True
                    ) as pbar:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    shutil.copyfileobj(r.raw, f)
    except requests.exceptions.RequestException:
        logging.exception(f"Failed to download {url} to {part_file.resolve()}")
        if part_file.exists():
            part_file.unlink()
        raise
    except KeyboardInterrupt:
        logging.info(f"Download of {url} to {part_file.resolve()} was cancelled")
        if part_file.exists():
            part_file.unlink()
        raise

    part_file.rename(local_file)


@contextmanager
def extract_matching_zip_file(
    zip_path: Path, pattern: str
) -> Generator[Path, None, None]:
    """
    Context manager that extracts a single file from a ZIP archive if its name matches
    a given regex pattern, using a temporary directory for extraction.

    Args:
        zip_path (Path): Path to the ZIP archive.
        pattern (str): Regex pattern to match against filenames in the archive.

    Yields:
        Path: Path to the extracted file inside the temporary directory.

    Example:
        with extract_matching_file(Path("archive.zip"), r"\\.iso$") as extracted:
            print(f"Extracted to: {extracted}")
    """
    regex = re.compile(pattern)

    with tempfile.TemporaryDirectory(prefix=f"sisou_{zip_path.name}_") as tmp_dir:
        tmp_path = Path(tmp_dir)

        with zipfile.ZipFile(zip_path, "r") as z:
            for name in z.namelist():
                if regex.search(name):
                    extracted_path = Path(z.extract(name, path=tmp_path))
                    yield extracted_path
                    break
            else:
                return


def download_file_to_tmp(url) -> Path:
    session = requests_cache.CachedSession(backend="memory")
    r = session.get(url)
    r.raise_for_status()

    sig_file = tempfile.NamedTemporaryFile(delete=False, prefix="sisou_", mode="wb")
    sig_file.write(r.content)
    sig_file.flush()
    sig_file.close()

    return Path(tempfile.gettempdir()) / sig_file.name


def format_size(bytes: int) -> str:
    """Format a file size in bytes into a human-readable string with appropriate units."""
    size: float = bytes
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
