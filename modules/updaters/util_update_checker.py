from functools import cache
import requests


@cache
def github_get_latest_version(owner: str, repo: str) -> dict:
    """Gets the latest version of a software via it's GitHub repository

    Args:
        owner (str): Owner of the repository
        repo (str): Name of the repository

    Returns:
        dict: the full release information
    """
    res = {}

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    release = requests.get(f"{api_url}/releases/latest").json()

    return release


def parse_github_release(release: dict) -> dict:
    """Parses a github release into a shorter, easier to read format

    Args:
        release (dict): Release information

    Returns:
        dict: The name of the tag, a dictionary representing {"filename": "url"},
    """
    res = {
        "tag": release["tag_name"],
        "files": {},
        "text": release["body"],
        "source_code": release["zipball_url"],
    }

    for asset in release["assets"]:
        res["files"][asset["name"]] = asset["browser_download_url"]

    return res
