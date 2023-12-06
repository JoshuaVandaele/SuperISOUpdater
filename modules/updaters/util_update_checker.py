from functools import cache
import requests


@cache
def github_get_latest_version(owner: str, repo: str) -> tuple[str, dict[str, str]]:
    """Gets the latest version of a software via it's GitHub repository

    Args:
        owner (str): Owner of the repository
        repo (str): Name of the repository

    Returns:
        tuple[str, dict[str, str]]: The name of the tag, and a dictionary representing {"filename": "url"}
    """
    res = {}

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    release = requests.get(f"{api_url}/releases/latest").json()
    for asset in release["assets"]:
        res[asset["name"]] = asset["browser_download_url"]

    return release["tag_name"], res
