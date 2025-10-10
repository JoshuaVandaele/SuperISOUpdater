import glob
import logging
import re
from abc import ABC
from pathlib import Path

from modules.exceptions import NoMirrorsError
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.Version import Version


class GenericUpdater(ABC):
    """
    Abstract base class for a generic updater that manages software updates.
    """

    def __init__(
        self, file_path: Path, mirror_mgr: GenericMirrorManager, *args, **kwargs
    ) -> None:
        """
        Initialize the GenericUpdater instance.

        Args:
            file_path (Path): The path to the file that needs to be updated.
            edition (str, optional): Edition of image to download. Requires `self.valid_edition: list[str]`.
            lang (str, optional): Language of image to download. Requires `self.valid_lang: list[str]`.
        """
        self.file_path = file_path.resolve()
        self.folder_path = self.file_path.parent
        self.mirror_mgr = mirror_mgr
        self.version_separator = mirror_mgr.current_mirror.version_separator

        if self.has_edition():
            if not "[[EDITION]]" in str(self.file_path):
                raise ValueError("Invalid name. The name needs a [[EDITION]] tag.")
            if self.edition.lower() not in (  # type: ignore
                valid_edition.lower() for valid_edition in self.valid_editions  # type: ignore
            ):
                raise ValueError(
                    f"Invalid edition. The available editions are: {', '.join(self.valid_editions)}."  # type: ignore
                )
            self.edition = next(
                valid_edition
                for valid_edition in self.valid_editions  # type: ignore
                if valid_edition.lower() == self.edition.lower()
            )

        if self.has_lang():
            if not "[[LANG]]" in str(self.file_path):
                raise ValueError("Invalid name. The name needs a [[LANG]] tag.")
            if self.lang.lower() not in (  # type: ignore
                valid_lang.lower() for valid_lang in self.valid_langs  # type: ignore
            ):
                raise ValueError(
                    f"Invalid language. The available languages are: {', '.join(self.valid_langs)}."  # type: ignore
                )
            self.lang = next(
                valid_lang
                for valid_lang in self.valid_langs  # type: ignore
                if valid_lang.lower() == self.lang.lower()
            )

        if self.has_arch():
            if not "[[ARCH]]" in str(self.file_path):
                raise ValueError("Invalid name. The name needs a [[ARCH]] tag.")
            if self.arch.lower() not in (  # type: ignore
                valid_arch.lower() for valid_arch in self.valid_archs  # type: ignore
            ):
                raise ValueError(
                    f"Invalid architecture. The available architectures are: {', '.join(self.valid_archs)}."  # type: ignore
                )
            self.arch = next(
                valid_arch
                for valid_arch in self.valid_archs  # type: ignore
                if valid_arch.lower() == self.arch.lower()
            )

        if not self.has_version():
            raise ValueError("Invalid name. The name needs a [[VER]] tag.")

        self.folder_path.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self) -> bool:
        """
        Check if there are updates available for the software.

        Returns:
            bool: True if updates are available, False if the local version is up to date.
        """
        if not (local_version := self._get_local_version()):
            logging.debug(
                f"[GenericUpdater.check_for_updates] No local version found for {self.__class__.__name__}"
            )
            return True

        is_update_available = local_version < self._get_latest_version()

        logging.debug(
            f"[GenericUpdater.check_for_updates] {local_version} < {self._get_latest_version()}? {is_update_available}"
        )
        return is_update_available

    def install_latest_version(self) -> None:
        """
        Install the latest version of the software.

        Raises:
            IntegrityCheckError: If the integrity check of the downloaded file fails.
        """
        old_file = self._get_local_file()
        new_file = self._get_complete_normalized_file_path(absolute=True)

        try:
            self.mirror_mgr.attempt_download(new_file)
        except NoMirrorsError as e:
            new_file.unlink(missing_ok=True)
            raise RuntimeError from e

        # If the installation was successful and we had a previous version installed, remove it
        if old_file:
            logging.debug(
                f"[GenericUpdater.install_latest_version] Removing old file: {old_file}"
            )
            old_file.unlink()

    def has_version(self) -> bool:
        """
        Check if the updater supports different versions.

        Returns:
            bool: True if different versions are supported, False otherwise.
        """
        return "[[VER]]" in str(self.file_path)

    def has_edition(self) -> bool:
        """
        Check if the updater supports different editions.

        Returns:
            bool: True if different editions are supported, False otherwise.
        """
        return hasattr(self, "edition") and hasattr(self, "valid_editions")

    def has_lang(self) -> bool:
        """
        Check if the updater supports different languages.

        Returns:
            bool: True if different languages are supported, False otherwise.
        """
        return hasattr(self, "lang") and hasattr(self, "valid_langs")

    def has_arch(self) -> bool:
        """
        Check if the updater supports different architectures.

        Returns:
            bool: True if different architectures are supported, False otherwise.
        """
        return hasattr(self, "arch") and hasattr(self, "valid_archs")

    def _get_local_file(self) -> Path | None:
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

        local_files = glob.glob(str(file_path).replace("[[VER]]", "*"))

        if local_files:
            return Path(local_files[0])
        logging.debug(
            f"[GenericUpdater._get_local_file] No local file found for {self.__class__.__name__}"
        )
        return None

    def _get_local_version(self) -> Version | None:
        """
        Get the version of the locally stored file by extracting the version number from the filename.

        Returns:
            list[str] | None: A list of integers representing the version number if found,
                            None if the version cannot be determined or no local file exists.
        """
        local_version: Version | None = None

        local_file = self._get_local_file()

        if not local_file or not self.has_version():
            logging.debug(
                f"[GenericUpdater._get_local_version] No local version found for {self.__class__.__name__}"
            )
            return None

        local_file_without_ext = local_file.with_suffix("")
        normalized_path_without_ext = Path(
            self._get_normalized_file_path(
                absolute=True,
                version=None,
                edition=self.edition if self.has_edition() else None,  # type: ignore
                lang=self.lang if self.has_lang() else None,  # type: ignore
            )
        ).with_suffix("")

        version_regex: str = r"(.+)".join(
            re.escape(part)
            for part in str(normalized_path_without_ext).split("[[VER]]")
        )
        local_version_regex = re.search(version_regex, str(local_file_without_ext))

        if local_version_regex:
            local_version = Version(
                local_version_regex.group(1),
                self.version_separator,
            )

        if not local_version:
            logging.debug(
                f"[GenericUpdater._get_local_version] No local version found for {self.__class__.__name__}"
            )

        return local_version

    def _get_latest_version(self) -> Version:
        return self.mirror_mgr.current_mirror.version

    def _get_normalized_file_path(
        self,
        absolute: bool,
        version: Version | None,
        edition: str | None = None,
        lang: str | None = None,
    ) -> Path:
        """
        Get the normalized file path with customizable version, edition, and language.

        Args:
            absolute (bool): If True, return the absolute file path. Otherwise, return the relative file path.
            version (Version): The version as a list of version components.
            edition (str, optional): The edition of the file. If provided, it replaces '[[EDITION]]' in the file name.
                                    Defaults to None.
            lang (str, optional): The language of the file. If provided, it replaces '[[LANG]]' in the file name.
                                    Defaults to None.

        Returns:
            Path: The normalized file path.

        Note:
            This method replaces placeholders such as '[[VER]]', '[[EDITION]]', and '[[LANG]]' in the file name
            with the specified version, edition, and language respectively. It also removes all spaces from the file name.
        """
        file_name: str = self.file_path.name

        # Replace placeholders with the specified version, edition, and language
        if version is not None and "[[VER]]" in file_name:
            file_name = file_name.replace("[[VER]]", str(version))

        if edition is not None and "[[EDITION]]" in file_name:
            file_name = file_name.replace("[[EDITION]]", edition)

        if lang is not None and "[[LANG]]" in file_name:
            file_name = file_name.replace("[[LANG]]", lang)

        # Remove all spaces from the file name
        file_name = "".join(file_name.split())

        # Return the absolute or relative file path based on the 'absolute' parameter
        return self.folder_path / file_name if absolute else Path(file_name)

    def _get_complete_normalized_file_path(
        self, absolute: bool, latest: bool = True
    ) -> Path:
        """
        Get the complete normalized file path with customizable version, edition, and language.

        Args:
            absolute (bool): If True, return the absolute file path. Otherwise, return the relative file path.
            latest (bool, optional): If True, use the latest version, edition, and language to construct the file path.
                                    If False, use the local version, edition, and language.
                                    Defaults to True.

        Returns:
            Path: The normalized file path.

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
