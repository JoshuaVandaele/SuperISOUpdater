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
        file_path (str): The path to the file that needs to be updated.
    """

    def __init__(self, file_path: str, *args, **kwargs) -> None:
        """
        Initialize the GenericUpdater instance.

        Args:
            file_path (str): The path to the file that needs to be updated.
        """
        self.file_path = os.path.abspath(file_path)
        self.folder_path = os.path.dirname(file_path)

        self.version_splitter = "."

        if self.has_edition():
            if self.edition.lower() not in (  # type: ignore
                valid_edition.lower() for valid_edition in self.valid_editions  # type: ignore
            ):
                raise ValueError(
                    f"Invalid edition. The available editions are: {', '.join(self.valid_editions)}."  # type: ignore
                )

        if self.has_lang():
            if self.lang.lower() not in (  # type: ignore
                valid_lang.lower() for valid_lang in self.valid_langs  # type: ignore
            ):
                raise ValueError(
                    f"Invalid language. The available languages are: {', '.join(self.valid_langs)}."  # type: ignore
                )

        os.makedirs(self.folder_path, exist_ok=True)

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
        new_file = self._get_complete_normalized_file_path(absolute=True)

        if not versioning_flag:
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

        if not integrity_check:
            # If integrity check failed, restore the old file or remove the new file
            if versioning_flag or not old_file:
                os.remove(new_file)
            else:
                os.replace(old_file, new_file)
            raise IntegrityCheckError("Integrity check failed: Hashes do not match")

        # If the installation was successful and we had a previous version installed, remove it
        if old_file:
            os.remove(old_file)

    def has_edition(self) -> bool:
        """
        Check if the updater supports different editions.

        Returns:
            bool: True if different editions are supported, False otherwise.
        """
        return (
            hasattr(self, "edition")
            and hasattr(self, "valid_editions")
            and "[[EDITION]]" in self.file_path
        )

    def has_lang(self) -> bool:
        """
        Check if the updater supports different languages.

        Returns:
            bool: True if different languages are supported, False otherwise.
        """
        return (
            hasattr(self, "lang")
            and hasattr(self, "valid_langs")
            and "[[LANG]]" in self.file_path
        )

    def _get_local_file(self) -> str | None:
        """
        Get the path of the locally stored file that matches the filename pattern.

        Returns:
            str | None: The path of the locally stored file if found, None if no file exists.
        """
        file_path = self._get_normalized_file_path(
            absolute=True,
            version=None,
            edition=self.edition if self.has_edition() else None,  # type: ignore
            lang=self.lang if self.has_lang() else None,  # type: ignore
        )

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

        if not local_file or "[[VER]]" not in self.file_path:
            return None

        normalized_path_without_ext: str = os.path.splitext(
            self._get_normalized_file_path(
                absolute=True,
                version=None,
                edition=self.edition if self.has_edition() else None,  # type: ignore
                lang=self.lang if self.has_lang() else None,  # type: ignore
            )
        )[0]

        version_regex: str = r"(.+)".join(
            re.escape(part) for part in normalized_path_without_ext.split("[[VER]]")
        )
        local_version_regex = re.search(version_regex, local_file)

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

    def _get_normalized_file_path(
        self,
        absolute: bool,
        version: list[str] | None = None,
        edition: str | None = None,
        lang: str | None = None,
    ) -> str:
        """
        Get the normalized file path with customizable version, edition, and language.

        Args:
            absolute (bool): If True, return the absolute file path. Otherwise, return the relative file path.
            version (list[str], optional): The version as a list of version components.
                                    If provided, it replaces '[[VER]]' in the file name.
                                    Defaults to None.
            edition (str, optional): The edition of the file. If provided, it replaces '[[EDITION]]' in the file name.
                                    Defaults to None.
            lang (str, optional): The language of the file. If provided, it replaces '[[LANG]]' in the file name.
                                    Defaults to None.

        Returns:
            str: The normalized file path.

        Note:
            This method replaces placeholders such as '[[VER]]', '[[EDITION]]', and '[[LANG]]' in the file name
            with the specified version, edition, and language respectively. It also removes all spaces from the file name.
        """
        file_name: str = os.path.basename(self.file_path)

        # Replace placeholders with the specified version, edition, and language
        if version is not None and "[[VER]]" in file_name:
            file_name = file_name.replace("[[VER]]", self._version_to_str(version))

        if edition is not None and "[[EDITION]]" in file_name:
            file_name = file_name.replace("[[EDITION]]", edition)

        if lang is not None and "[[LANG]]" in file_name:
            file_name = file_name.replace("[[LANG]]", lang)

        # Remove all spaces from the file name
        file_name = "".join(file_name.split())

        # Return the absolute or relative file path based on the 'absolute' parameter
        return os.path.join(self.folder_path, file_name) if absolute else file_name

    def _get_complete_normalized_file_path(self, absolute: bool, latest: bool = True):
        """
        Get the complete normalized file path with customizable version, edition, and language.

        Args:
            absolute (bool): If True, return the absolute file path. Otherwise, return the relative file path.
            latest (bool, optional): If True, use the latest version, edition, and language to construct the file path.
                                    If False, use the local version, edition, and language.
                                    Defaults to True.

        Returns:
            str: The normalized file path.

        Note:
            This method replaces placeholders such as '[[VER]]', '[[EDITION]]', and '[[LANG]]' in the file name
            with the specified version, edition, and language respectively. It also removes all spaces from the file name.
        """
        return self._get_normalized_file_path(
            absolute=absolute,
            version=self._get_latest_version() if latest else self._get_local_version(),
            edition=self.edition if self.has_edition() else None,  # type: ignore
            lang=self.lang if self.has_lang() else None,  # type: ignore
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

    def _str_to_version(self, version_str: str):
        """
        Convert a version string to a list of version components.

        Args:
            version_str (str): The version as a string.

        Returns:
            list[str]: The version as a list of version components.
        """
        return [
            version_number.strip()
            for version_number in version_str.split(self.version_splitter)
        ]

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
