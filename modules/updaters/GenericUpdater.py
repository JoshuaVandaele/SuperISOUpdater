import glob
import logging
import os
import re
from abc import ABC
from pathlib import Path

from modules.exceptions import NoMirrorsError
from modules.ISOPath import ISOPath
from modules.mirrors.GenericMirrorManager import GenericMirrorManager
from modules.Version import Version


class GenericUpdater(ABC):
    """
    Abstract base class for a generic updater that manages software updates.
    """

    def __init__(
        self,
        iso_path: ISOPath,
        mirror_mgr: GenericMirrorManager,
        arch: str | None = None,
        edition: str | None = None,
        lang: str | None = None,
        extension: str = "iso",
        valid_archs: list[str] | None = None,
        valid_editions: list[str] | None = None,
        valid_langs: list[str] | None = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Initialize the GenericUpdater instance.

        Args:
            iso_path (ISOPath): The path to the ISO file that needs to be updated.
            mirror_mgr (GenericMirrorManager): The mirror manager. This should be provided by the child class.
            arch (str | None): The architecture for which the ISO is intended. Only useful if `valid_archs` is defined.
            edition (str | None): The edition of the software. Only useful if `valid_editions` is defined.
            lang (str | None): The language of the software. Only useful if `valid_langs` is defined.
            extension (str): The file extension to use. Defaults to 'iso'.
            valid_archs (list[str] | None): A list of valid architectures.
            valid_editions (list[str] | None): A list of valid editions.
            valid_langs (list[str] | None): A list of valid languages.
        """

        self.iso_path = iso_path
        self.mirror_mgr = mirror_mgr
        self.version_separator = mirror_mgr.current_mirror.version_separator
        self.extension = extension

        if edition:
            if not valid_editions:
                raise ValueError("The child class needs to define valid editions.")
            if not self.iso_path.has_edition():
                raise ValueError("Invalid name. The name needs a [[EDITION]] tag.")

            if edition.lower() not in (
                valid_edition.lower() for valid_edition in valid_editions
            ):
                raise ValueError(
                    f"Invalid edition. The available editions are: {', '.join(valid_editions)}."
                )
            self.edition = next(
                valid_edition
                for valid_edition in valid_editions
                if valid_edition.lower() == edition.lower()
            )
        else:
            self.edition = None

        if lang:
            if not self.iso_path.has_lang():
                raise ValueError("Invalid name. The name needs a [[LANG]] tag.")
            if not valid_langs:
                raise ValueError("The child class needs to define valid languages.")

            if lang.lower() not in (valid_lang.lower() for valid_lang in valid_langs):
                raise ValueError(
                    f"Invalid language. The available languages are: {', '.join(valid_langs)}."
                )
            self.lang = next(
                valid_lang
                for valid_lang in valid_langs
                if valid_lang.lower() == lang.lower()
            )
        else:
            self.lang = None

        if arch:
            if not self.iso_path.has_arch():
                raise ValueError("Invalid name. The name needs a [[ARCH]] tag.")
            if not valid_archs:
                raise ValueError("The child class needs to define valid architectures.")

            if arch.lower() not in (valid_arch.lower() for valid_arch in valid_archs):
                raise ValueError(
                    f"Invalid architecture. The available architectures are: {', '.join(valid_archs)}."
                )
            self.arch = next(
                valid_arch
                for valid_arch in valid_archs
                if valid_arch.lower() == arch.lower()
            )
        else:
            self.arch = None

        os.makedirs(self.iso_path.dirname(), exist_ok=True)

    def is_update_available(self) -> bool:
        """
        Check if there are updates available for the software.

        Returns:
            bool: True if updates are available, False if the local version is up to date.
        """
        if not (local_version := self._get_local_version()):
            logging.debug(
                f"[GenericUpdater.is_update_available] No local version found for {self.__class__.__name__}"
            )
            return True

        is_update_available = local_version < self._get_latest_version()

        logging.debug(
            f"[GenericUpdater.is_update_available] {local_version} < {self._get_latest_version()}? {is_update_available}"
        )
        return is_update_available

    def install_latest_version(self) -> None:
        """
        Install the latest version of the software.

        Raises:
            IntegrityCheckError: If the integrity check of the downloaded file fails.
        """
        old_file = self._get_local_file()
        new_file = Path(
            self.iso_path.fill_placeholders(
                version=str(self._get_latest_version()),
                edition=self.edition,
                lang=self.lang,
                arch=self.arch,
                extension=self.extension,
            )
        )

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

    def _get_local_file(self) -> Path | None:
        """
        Get the path of the locally stored file that matches the filename pattern.

        Returns:
            str | None: The path of the locally stored file if found, None if no file exists.
        """
        file_path = self.iso_path.fill_placeholders(
            version="*",  # Use wildcard to match any version in the local file name
            edition=self.edition,
            lang=self.lang,
            arch=self.arch,
            extension=self.extension,
        )

        local_files = glob.glob(file_path)

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

        if not local_file:
            logging.debug(
                f"[GenericUpdater._get_local_version] No local version found for {self.__class__.__name__}"
            )
            return None

        local_file_without_ext = local_file.with_suffix("")
        normalized_path_without_ver = self.iso_path.basename().fill_placeholders(
            version=None, edition=self.edition, lang=self.lang, arch=self.arch
        )

        version_regex: str = r"(.+)".join(
            re.escape(part) for part in normalized_path_without_ver.split("[[VER]]")
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
