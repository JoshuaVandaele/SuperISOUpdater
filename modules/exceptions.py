class DownloadLinkNotFoundError(Exception):
    """
    Custom exception to represent an error when the download link for a file is not found.
    """

    pass


class VersionNotFoundError(Exception):
    """
    Custom exception to represent an error when a specific version is not found.
    This exception can be raised when a program is unable to find a specific version of a resource.

    Example:
        try:
            version = GenericUpdater._get_latest_version()
        except VersionNotFoundError as e:
            print(f"Error: {e}")
    """

    pass


class IntegrityCheckError(Exception):
    """
    Custom exception to represent an error when an integrity check fails.
    This exception can be raised when a program performs an integrity check (e.g., hash verification) on a file,
    and the check fails, indicating that the file's content may have been altered or corrupted.

    Example:
        if not md5_hash_check(file, expected_md5_hash):
            raise IntegrityCheckError("MD5 hash verification failed.")
    """

    pass
