import logging
import traceback
from abc import ABC
from pathlib import Path
from typing import Callable

from modules.exceptions import NoMirrorsError
from modules.mirrors.GenericMirror import GenericMirror
from modules.Version import Version


class GenericMirrorManager(ABC):
    """
    A class representing a mirror for downloading files.
    This class fetches a web page, determines the type of checksum available,
    and retrieves the checksum value from the page.
    It is intended to be used as a base class for specific mirror implementations.
    """

    def __init__(
        self,
        mirrors: list[GenericMirror],
    ) -> None:
        """
        Initializes the GenericMirrorManager with a list of mirrors.

        Args:
            mirrors (list[GenericMirror]): A list of GenericMirror instances.
        """
        self._mirrors: list[GenericMirror] = mirrors

        self._initialize_all_mirrors()
        self._ensure_latest_version()
        self._mirrors.sort(key=lambda m: m.speed, reverse=True)

    @property
    def current_mirror(self):
        return self._mirrors[0]

    def try_for_all_mirrors(
        self,
        func: Callable,
        args: tuple = (),
        check_bool_output: bool = False,
        stop_after_success: bool = False,
    ) -> None:
        """
        Attempts to run a function on all mirrors.
        Those that fail will be removed.

        Args:
            func (Callable): Function to call
            args (tuple): Arguments to pass to the function
            check_bool_output (bool, optional): Should we check the function's output to treat it as a success? Defaults to False.
            stop_after_success (bool, optional): Should we stop after the first success? Defaults to False.

        Raises:
            NoMirrorsError: If all mirrors fail
        """
        failed_mirrors: list[tuple] = []
        mirror_copy = self._mirrors.copy()
        for mirror in mirror_copy:
            try:
                bool_output = func(mirror, *args)
                if check_bool_output and not bool_output:
                    raise RuntimeError(f"Returned non-true output: {bool_output}")
                if stop_after_success:
                    break
            except Exception as e:
                self._mirrors.remove(mirror)
                failed_mirrors.append((mirror, e))
                logging.debug(f"Error with mirror {mirror._url}: {e}")

        if not self._mirrors:
            err_details = [
                f"{m._url}: {''.join(traceback.format_exception(type(e), e, e.__traceback__))}"
                for m, e in failed_mirrors
            ]
            raise NoMirrorsError(
                f"All mirrors failed to run {func.__name__}. Errors: {'\n'.join(err_details)}"
            )

    def _initialize_all_mirrors(self) -> None:
        """
        Attempts to initialize all mirrors.
        Those that fail will be removed.
        """
        self.try_for_all_mirrors(lambda m: m.initialize())

    def _ensure_latest_version(self) -> None:
        """
        Ensures that the mirrors all share the same latest version.
        Those that do not will be removed.
        """
        latest_version: Version = max(mirror.version for mirror in self._mirrors)
        self.try_for_all_mirrors(
            lambda m: m.version == latest_version, check_bool_output=True
        )

    def attempt_download(self, local_file: Path) -> None:
        self.try_for_all_mirrors(
            lambda m: m.download_and_verify(local_file),
            check_bool_output=True,
            stop_after_success=True,
        )
