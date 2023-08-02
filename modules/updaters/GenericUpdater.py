import glob
import logging
import os
import re
from abc import ABC, abstractmethod

from modules.exceptions import IntegrityCheckError
from modules.utils import download_file


class GenericUpdater(ABC):
    """
    Abstract base class for a generic updater that manages software updates.

    Attributes:
    """

    def __init__(self, file_path: str, *args, **kwargs) -> None:
        """
        Initialize the GenericUpdater instance.

        Args:
            file_path (str): The path to the file that needs to be updated.
        """
        self.file_path = os.path.abspath(file_path)
        self.folder_path = os.path.dirname(self.file_path)
        self.version_splitter = "."

        if self.has_edition():
            if self.edition.lower() not in (  # type: ignore
                valid_edition.lower() for valid_edition in self.valid_editions  # type: ignore
            ):
                raise ValueError(
                    f"Invalid edition. The available editions are: {', '.join(self.valid_editions)}."  # type: ignore
                )

        os.makedirs(self.folder_path, exist_ok=True)

    def install_latest_version(self) -> None:
        """
        Install the latest version of the software.

        Raises:
            IntegrityCheckError: If the integrity check of the downloaded file fails.
        """
        download_link = self._get_download_link()
        versioning_flag: bool = "[[VER]]" in self.file_path

        # Determine the old and new file paths
        old_file = self._get_local_file()
        if versioning_flag:
            new_file = self._get_versioned_latest_file_name(absolute=True, edition=True)
        else:
            if self.has_edition():
                new_file = self._get_editioned_file_name(absolute=True)
            else:
                new_file = self.file_path

            # If the file is being replaced, back it up
            if old_file:
                old_file += ".old"
                os.replace(self.file_path, old_file)

        download_file(download_link, new_file)

        # Check the integrity of the downloaded file
        try:
            integrity_check = self.check_integrity()
        except Exception as e:
            # If integrity check failed, restore the old file or remove the new file
            if versioning_flag or not old_file:
                os.remove(new_file)
            else:
                os.replace(old_file, new_file)
            raise IntegrityCheckError(
                "Integrity check failed: An error occurred"
            ) from e

        if not self.check_integrity():
            # If integrity check failed, restore the old file or remove the new file
            if versioning_flag or not old_file:
                os.remove(new_file)
            else:
                os.replace(old_file, new_file)
            raise IntegrityCheckError("Integrity check failed: Hashes do not match")

        # If the installation was successful and we had a previous version installed, remove it
        if old_file:
            os.remove(old_file)

    @abstractmethod
    def _get_download_link(self) -> str:
        """
        (Protected) Get the download link for the latest version of the software.

        Returns:
            str: The download link for the latest version of the software.

        Raises:
            DownloadLinkNotFoundError: If the download link is not found.
        """
        pass

    @abstractmethod
    def check_integrity(self) -> bool:
        """
        Check the integrity of the downloaded software.

        Returns:
            bool: True if the downloaded software is valid, otherwise False.
        """
        pass

    def check_for_updates(self) -> bool:
        """
        Check if there are updates available for the software.

        Returns:
            bool: True if updates are available, False if the local version is up to date.
        """
        if not (local_version := self._get_local_version()):
            return True

        is_update_available = self._compare_version_numbers(
            local_version, self._get_latest_version()
        )
        logging.debug(
            f"[GenericUpdater.check_for_updates] {self._version_to_str(local_version)} > {self._version_to_str(self._get_latest_version())}? {is_update_available}"
        )
        return is_update_available

    @staticmethod
    def _compare_version_numbers(
        old_version: list[str], new_version: list[str]
    ) -> bool:
        """
        Compare version numbers to check if a new version is available.

        Args:
            old_version (list[str]): The old version as a list of version components.
            new_version (list[str]): The new version as a list of version components.

        Returns:
            bool: True if the new version is greater than the old version, False otherwise.
        """
        for i in range(len(new_version)):
            try:
                if int(new_version[i]) > int(old_version[i]):
                    return True
            except ValueError:
                if int(new_version[i], 32) > int(old_version[i], 32):
                    return True
            except IndexError:
                return True
        return False

    def _get_local_file(self) -> str | None:
        """
        Get the path of the locally stored file that matches the filename pattern.

        Returns:
            str | None: The path of the locally stored file if found, None if no file exists.
        """
        if self.has_edition():
            file_path = self._get_editioned_file_name(absolute=True)
        else:
            file_path = self.file_path
        local_files = glob.glob(file_path.replace("[[VER]]", "*"))

        if local_files:
            return local_files[0]
        return None

    def _get_local_version(self) -> list[str] | None:
        """
        Get the version of the locally stored file by extracting the version number from the filename.

        Returns:
            list[str] | None: A list of integers representing the version number if found,
                            None if the version cannot be determined or no local file exists.
        """
        local_version: list[str] | None = None

        local_file = self._get_local_file()

        if not local_file or "[[VER]]" not in self._get_editioned_file_name():
            return None

        local_version_regex = re.search(
            self._get_editioned_file_name().replace("[[VER]]", r"(.+)"),
            local_file,
        )

        if local_version_regex:
            local_version = self._str_to_version(local_version_regex.group(1))
        return local_version

    def _get_latest_version(self) -> list[str]:
        """
        Get the latest version of the software from the download page.

        Returns:
            list[str]: A list of integers representing the latest version number.

        Raises:
            VersionNotFoundError: If the latest version cannot be found on the download page.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} has not been implemented yet."
        )

    def _version_to_str(self, version: list[str]):
        """
        Convert a list of version components to a version string.

        Args:
            version (list[str]): The version as a list of version components.

        Returns:
            str: The version as a string with components joined by the version splitter.
        """
        return self.version_splitter.join(str(i) for i in version)

    def _get_versioned_file_name(
        self, version: list[str], absolute: bool = False, edition: bool = False
    ) -> str:
        """
        Get the file name with version components replaced by the specified version.

        Args:
            version (list[str]): The version as a list of version components.
            absolute (bool, optional): If True, return the absolute file path. Defaults to False.
            edition (bool, optional): If True, add the edition to the file name as well. Defaults to False.

        Returns:
            str: The versioned file name.
        """
        file_name = self.file_path if absolute else os.path.basename(self.file_path)
        if "[[VER]]" in file_name:
            file_name = file_name.replace("[[VER]]", self._version_to_str(version))
        if self.has_edition() and edition:
            file_name = file_name.replace("[[EDITION]]", self.edition)  # type: ignore
        return file_name

    def _get_versioned_local_file_name(
        self, absolute: bool = False, edition: bool = False
    ) -> str | None:
        """
        Get the versioned local file name if it exists.

        Args:
            absolute (bool, optional): If True, return the absolute file path. Defaults to False.
            edition (bool, optional): If True, add the edition to the file name as well. Defaults to False.

        Returns:
            str | None: The versioned local file name or None if no local version exists.
        """
        local_version = self._get_local_version()
        if local_version:
            return self._get_versioned_file_name(local_version, absolute, edition)
        return None

    def _get_versioned_latest_file_name(
        self, absolute: bool = False, edition: bool = False
    ) -> str:
        """
        Get the versioned latest file name.

        Args:
            absolute (bool, optional): If True, return the absolute file path. Defaults to False.
            edition (bool, optional): If True, add the edition to the file name as well. Defaults to False.

        Returns:
            str: The versioned latest file name.
        """
        return self._get_versioned_file_name(
            self._get_latest_version(), absolute, edition
        )

    def _str_to_version(self, version_str: str):
        return [
            version_number.strip()
            for version_number in version_str.split(self.version_splitter)
        ]

    def has_edition(self) -> bool:
        return (
            hasattr(self, "edition")
            and hasattr(self, "valid_editions")
            and "[[EDITION]]" in self.file_path
        )

    def _get_editioned_file_name(self, absolute: bool = False) -> str:
        file_name = self.file_path if absolute else os.path.basename(self.file_path)

        if not self.has_edition():
            return file_name

        return file_name.replace("[[EDITION]]", self.edition)  # type: ignore
