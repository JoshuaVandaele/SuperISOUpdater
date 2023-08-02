import hashlib
import logging
import os
import re
import shutil
import traceback
import uuid

import requests
import tomllib
from bs4 import BeautifulSoup, Tag


def logging_critical_exception(msg, *args, **kwargs):
    """
    Log a critical exception with traceback information.

    Args:
        msg (str): The error message to be logged.
        *args: Variable length argument list to be passed to the logging.critical method.
        **kwargs: Keyword arguments to be passed to the logging.critical method.
    """
    logging.critical(f"{msg}\n{traceback.format_exc()}", *args, **kwargs)


def parse_config(toml_file: str) -> dict | None:
    """Parse a TOML configuration file and return a dictionary representation.

    Args:
        toml_file (str): The path to the TOML configuration file.

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
            if "directory" in value:
                new_key = value["directory"]
                del value["directory"]
            else:
                new_key = key
            new_dict[new_key] = parse_config_from_dict(value)
        elif key == "enabled":
            if value == True:
                continue
            else:
                return
        else:
            new_dict[key] = value
    return new_dict


def md5_hash_check(file: str, hash: str) -> bool:
    """
    Calculate the MD5 hash of a given file and compare it with a provided hash value.

    Args:
        file (str): The path to the file for which the hash is to be calculated.
        hash (str): The MD5 hash value to compare against the calculated hash.

    Returns:
        bool: True if the calculated MD5 hash matches the provided hash; otherwise, False.
    """
    with open(file, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    result = hash.lower() == file_hash.hexdigest()

    logging.debug(
        f"[md5_hash_check] {os.path.abspath(file)}: `{hash}` is equal to `{file_hash.hexdigest()}`? {result}"
    )
    return result


def sha256_hash_check(file: str, hash: str) -> bool:
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
        while chunk := f.read(8192):
            file_hash.update(chunk)
    result = hash.lower() == file_hash.hexdigest()

    logging.debug(
        f"[sha256_hash_check] {os.path.abspath(file)}: `{hash.lower()}` is equal to `{file_hash.hexdigest()}`? {result}"
    )
    return result


def sha512_hash_check(file: str, hash: str) -> bool:
    """
    Calculate the SHA-512 hash of a given file and compare it with a provided hash value.

    Args:
        file (str): The path to the file for which the hash is to be calculated.
        hash (str): The SHA-512 hash value to compare against the calculated hash.

    Returns:
        bool: True if the calculated SHA-512 hash matches the provided hash; otherwise, False.
    """
    with open(file, "rb") as f:
        file_hash = hashlib.sha512()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    result = hash.lower() == file_hash.hexdigest()

    logging.debug(
        f"[sha512_hash_check] {os.path.abspath(file)}: `{hash.lower()}` is equal to `{file_hash.hexdigest()}`? {result}"
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
    return next(
        line.split()[hash_position_in_line]
        for line in hashes.strip().splitlines()
        if all(match in line for match in match_strings_in_line)
    )


def download_file(url: str, local_file: str) -> None:
    """
    Download a file from a given URL and save it to the local file system.

    Args:
        url (str): The URL of the file to download.
        local_file (str): The path where the downloaded file will be saved on the local file system.

    Returns:
        None
    """
    logging.debug(f"[download_file] Downloading {url} to {os.path.abspath(local_file)}")
    with requests.get(url, stream=True) as r:
        with open(local_file, "wb") as f:
            shutil.copyfileobj(r.raw, f)


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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "referer": "localhost",
    }
    session_id = uuid.uuid4()

    r = requests.get(url, headers=headers)

    matches = re.search(r'<option value="([0-9]+)">Windows', r.text)
    if not matches or not matches.groups():
        raise LookupError("Could not find product edition id")

    product_edition_id = matches.group(1)

    logging.debug(
        f"[windows_consumer_download] Product edition id: `{product_edition_id}`"
    )

    # Permit Session ID
    r = requests.get(
        f"https://vlscppe.microsoft.com/tags?org_id=y6jn8c31&session_id={session_id}",
        headers=headers,
    )

    language_skuID_table_html_url = f"https://www.microsoft.com/en-US/api/controls/contentinclude/html?pageId=a8f8f489-4c7f-463a-9ca6-5cff94d8d041&host=www.microsoft.com&segments=software-download,{url_segment}&query=&action=getskuinformationbyproductedition&sessionId={session_id}&productEditionId={product_edition_id}&sdVersion=2"

    language_skuID_table_html = requests.get(
        language_skuID_table_html_url, headers=headers
    )

    sku_id = "".join(
        filter(
            str.isdigit,
            next(
                table_line
                for table_line in language_skuID_table_html.text.splitlines()
                if lang in table_line
            ),
        )
    )

    logging.debug(f"[windows_consumer_download] Found SKU ID {sku_id} for {lang}")

    # Get ISO download link page
    iso_download_link_page = f"https://www.microsoft.com/en-US/api/controls/contentinclude/html?pageId=6e2a1789-ef16-4f27-a296-74ef7ef5d96b&host=www.microsoft.com&segments=software-download,{url_segment}&query=&action=GetProductDownloadLinksBySku&sessionId={session_id}&skuId={sku_id}&language={lang}&sdVersion=2"
    r = requests.get(iso_download_link_page, headers=headers)

    s = BeautifulSoup(r.content, features="lxml")

    hash_table: Tag | None = s.find("table", "table-bordered")  # type: ignore
    if not hash_table:
        raise LookupError(
            "Could not find table containing SHA256 hashes. (Are you being rate limited?)"
        )

    next_is_result = False
    result: Tag | None = None
    for tr in hash_table.find_all("tr"):
        if result:
            break
        for td in tr.find_all("td"):
            if next_is_result:
                result = td
                break
            if lang in td.getText():
                next_is_result = True
    if not result:
        raise LookupError(
            "Could not find row containing SHA256 hashes. (Are you being rate limited?)"
        )

    hash = result.getText()

    download_a_tag: Tag | None = s.find(
        "a", href=True, attrs={"class": "button button-long button-flat button-purple"}
    )  # type: ignore
    if not download_a_tag:
        raise LookupError(
            "Could not find tag containing the download link. (Are you being rate limited?)"
        )
    download_link: str = download_a_tag.get("href")  # type: ignore

    return download_link, hash
