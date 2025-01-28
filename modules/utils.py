import hashlib
import logging
import re
import shutil
import tomllib
import traceback
import uuid
from pathlib import Path

import requests
from pgpy import PGPKey, PGPSignature
from tqdm import tqdm

READ_CHUNK_SIZE = 524288


def logging_critical_exception(msg, *args, **kwargs):
    """
    Log a critical exception with traceback information.

    Args:
        msg (str): The error message to be logged.
        *args: Variable length argument list to be passed to the logging.critical method.
        **kwargs: Keyword arguments to be passed to the logging.critical method.
    """
    logging.critical(f"{msg}\n{traceback.format_exc()}", *args, **kwargs)


def parse_config(toml_file: Path) -> dict | None:
    """Parse a TOML configuration file and return a dictionary representation.

    Args:
        toml_file (Path): The path to the TOML configuration file.

    Returns:
        dict | None: The parsed configuration as a dictionary, or None if there was an error during parsing.
    """
    with open(toml_file, "rb") as f:
        toml_dict = tomllib.load(f)
    return parse_config_from_dict(toml_dict)


def parse_config_from_dict(input_dict: dict):
    """Recursively parse the nested config dictionary and return a new dictionary where the keys are the directory, unless they are a module's name.

    Args:
        input_dict (dict): The input dictionary to be parsed.

    Returns:
        dict: The parsed dictionary with modified keys.
    """
    new_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            if "enabled" in value and not value["enabled"]:
                logging.debug(f"Skipping disabled module {key}")
                del value
                continue
            if "directory" in value:
                logging.debug(f"Found directory {value['directory']}")
                new_key = value["directory"]
                del value["directory"]
            else:
                logging.debug(f"Found module {key}")
                new_key = key
            new_dict[new_key] = parse_config_from_dict(value)
        elif key == "enabled":
            continue
        else:
            logging.debug(f"Found key {key}")
            new_dict[key] = value
    return new_dict


def md5_hash_check(file: Path, hash: str) -> bool:
    """
    Calculate the MD5 hash of a given file and compare it with a provided hash value.

    Args:
        file (Path): The path to the file for which the hash is to be calculated.
        hash (str): The MD5 hash value to compare against the calculated hash.

    Returns:
        bool: True if the calculated MD5 hash matches the provided hash; otherwise, False.
    """
    with open(file, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(READ_CHUNK_SIZE):
            file_hash.update(chunk)
    result = hash.lower() == file_hash.hexdigest()

    logging.debug(
        f"[md5_hash_check] {file.resolve()}: `{hash.lower()}` is {'' if result else 'not'} equal to file hash `{file_hash.hexdigest()}`"
    )
    return result


def sha1_hash_check(file: Path, hash: str) -> bool:
    """
    Calculate the SHA-1 hash of a given file and compare it with a provided hash value.

    Args:
        file (Path): The path to the file for which the hash is to be calculated.
        hash (str): The SHA-1 hash value to compare against the calculated hash.

    Returns:
        bool: True if the calculated SHA-1 hash matches the provided hash; otherwise, False.
    """
    with open(file, "rb") as f:
        file_hash = hashlib.sha1()
        while chunk := f.read(READ_CHUNK_SIZE):
            file_hash.update(chunk)
    result = hash.lower() == file_hash.hexdigest()

    logging.debug(
        f"[sha1_hash_check] {file.resolve()}: `{hash.lower()}` is {'' if result else 'not'} equal to file hash `{file_hash.hexdigest()}`"
    )
    return result


def sha256_hash_check(file: Path, hash: str) -> bool:
    """
    Calculate the SHA-256 hash of a given file and compare it with a provided hash value.

    Args:
        file (str): The path to the file for which the hash is to be calculated.
        hash (str): The SHA-256 hash value to compare against the calculated hash.

    Returns:
        bool: True if the calculated SHA-256 hash matches the provided hash; otherwise, False.
    """
    with open(file, "rb") as f:
        file_hash = hashlib.sha256()
        while chunk := f.read(READ_CHUNK_SIZE):
            file_hash.update(chunk)
    result = hash.lower() == file_hash.hexdigest()

    logging.debug(
        f"[sha256_hash_check] {file.resolve()}: `{hash.lower()}` is {'' if result else 'not'} equal to file hash `{file_hash.hexdigest()}`"
    )
    return result


def sha512_hash_check(file: Path, hash: str) -> bool:
    """
    Calculate the SHA-512 hash of a given file and compare it with a provided hash value.

    Args:
        file (Path): The path to the file for which the hash is to be calculated.
        hash (str): The SHA-512 hash value to compare against the calculated hash.

    Returns:
        bool: True if the calculated SHA-512 hash matches the provided hash; otherwise, False.
    """
    with open(file, "rb") as f:
        file_hash = hashlib.sha512()
        while chunk := f.read(READ_CHUNK_SIZE):
            file_hash.update(chunk)
    result = hash.lower() == file_hash.hexdigest()

    logging.debug(
        f"[sha512_hash_check] {file.resolve()}: `{hash.lower()}` is {'' if result else 'not'} equal to file hash `{file_hash.hexdigest()}`"
    )
    return result


def pgp_check(file_path: Path, signature: str | bytes, public_key: str | bytes) -> bool:
    """Verifies the signature of a file against a publick ey

    Args:
        file_path (Path): Path to the file to check
        signature (str | bytes): Signature
        public_key (str | bytes): Public Key

    Raises:
        ValueError: If the supplied public key is invalid
        ValueError: If the supplied signature is invalid

    Returns:
        bool: Weither the check was successful or not
    """
    pub_key = PGPKey.from_blob(public_key)
    sig = PGPSignature.from_blob(signature)

    if not pub_key:
        raise ValueError(f"Invalid pub_key: {public_key}")
    elif not sig:
        raise ValueError(f"Invalid signature: {signature}")

    # For some reason, from_blob can return either a tuple with either [ThingIwant, Literally Nothing] or directly ThingIWant
    if isinstance(pub_key, tuple):
        pub_key = pub_key[0]
    if isinstance(sig, tuple):
        sig = sig[0]

    with open(file_path, "rb") as f:
        file_content = f.read()

    result = bool(pub_key.verify(file_content, sig))

    logging.debug(
        f"[pgp_check] {file_path.resolve()}: Signature is {'' if result else 'not'} valid"
    )

    return result


def parse_hash(
    hashes: str, match_strings_in_line: list[str], hash_position_in_line: int
):
    """Parse a list of hashes and extract a specific hash based on matching strings.

    Args:
        hashes (str): A string containing a list of hashes.
        match_strings_in_line (list[str]): List of strings that must be present in the line to consider it.
        hash_position_in_line (int): The position of the desired hash in each line.

    Returns:
        The extracted hash value.
    """
    logging.debug(
        f"[parse_hash] Parsing hashes with match strings `{match_strings_in_line}` and hash position {hash_position_in_line} in those hashes:\n{hashes}"
    )
    hash = next(
        line.split()[hash_position_in_line]
        for line in hashes.strip().splitlines()
        if all(match in line for match in match_strings_in_line)
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


def windows_consumer_download(
    windows_version: str = "11", lang="English International"
) -> tuple[str, str]:
    """
    Obtain a Windows ISO download URL for a specific Windows version and language.

    Args:
        windows_version (str): The desired Windows version. Valid options are '11', '10', or '8'.
                            Default is '11'.
        lang (str): The desired language for the Windows ISO. Default is 'English International'.
            See https://www.microsoft.com/en-us/software-download/windows11 for a list of available languages

    Returns:
        tuple[str, str]: A tuple containing the download link and the SHA256 hash of the downloaded file.
    """
    # Thanks https://github.com/pbatard/Fido/ for already having done the reverse-engineering for me <3
    match windows_version:
        case "11":
            url_segment = f"windows{windows_version}"
        case "10":
            url_segment = f"windows{windows_version}ISO"
        case "8":
            url_segment = f"windows{windows_version}ISO"
        case _:
            raise NotImplementedError(
                "The valid windows versions are '11', '10', or '8'."
            )

    url = f"https://www.microsoft.com/en-us/software-download/{url_segment}"
    PROFILE_ID = "606624d44113"
    ORG_ID = "y6jn8c31"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "referer": "localhost",
    }
    session_id = uuid.uuid4()

    iso_download_link = requests.get(url, headers=headers)

    matches = re.search(r'<option value="([0-9]+)">Windows', iso_download_link.text)
    if not matches or not matches.groups():
        raise LookupError("Could not find product edition id")

    product_edition_id = matches.group(1)
    logging.debug(
        f"[windows_consumer_download] Product edition id: `{product_edition_id}`"
    )

    matches = re.search(
        rf"FileHash(.+\n+)+?^<\/tr>.+{lang}.+\n<td>(.+)<",
        iso_download_link.text,
        re.MULTILINE,
    )

    if not matches or not matches.groups():
        raise LookupError("Could not find SHA256 hash")

    hash = matches.group(2)
    logging.debug(f"[windows_consumer_download] Found hash: `{hash}`")

    # Permit Session ID
    requests.get(
        f"https://vlscppe.microsoft.com/tags?org_id={ORG_ID}&session_id={session_id}"
    )

    language_skuID_table_url = (
        "https://www.microsoft.com/software-download-connector/api/getskuinformationbyproductedition"
        + f"?profile={PROFILE_ID}"
        + f"&productEditionId={product_edition_id}"
        + f"&SKU=undefined"
        + f"&friendlyFileName=undefined"
        + f"&Locale=en-US"
        + f"&sessionID={session_id}"
    )

    language_skuID_table = requests.get(
        language_skuID_table_url, headers=headers
    ).json()

    sku_id = None

    for sku in language_skuID_table["Skus"]:
        if sku["Language"] == lang:
            sku_id = sku["Id"]

    if not sku_id:
        raise ValueError(f"The language '{lang}' for Windows could not be found!")

    logging.debug(f"[windows_consumer_download] Found SKU ID {sku_id} for {lang}")

    # Get ISO download link page
    iso_download_link_page = (
        "https://www.microsoft.com/software-download-connector/api/GetProductDownloadLinksBySku"
        + f"?profile={PROFILE_ID}"
        + "&productEditionId=undefined"
        + f"&SKU={sku_id}"
        + "&friendlyFileName=undefined"
        + f"&Locale=en-US"
        + f"&sessionID={session_id}"
    )

    iso_download_link_json = requests.get(
        iso_download_link_page, headers=headers
    ).json()

    if "Errors" in iso_download_link_json:
        raise RuntimeError(f"Errors from Microsoft: {iso_download_link_json["Errors"]}")

    download_link = iso_download_link_json["ProductDownloadOptions"][0]["Uri"]

    return download_link, hash
