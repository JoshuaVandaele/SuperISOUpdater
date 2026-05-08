import os
import tomllib
from abc import ABCMeta
from dataclasses import dataclass
from functools import cache
from sys import modules
from typing import Type

import modules.updaters
from modules.ISOPath import ISOPath
from modules.updaters import GenericUpdater


@dataclass
class ISOConfig:
    iso_path: ISOPath
    updater: Type[GenericUpdater]
    archs: list[str] | None = None
    editions: list[str] | None = None
    langs: list[str] | None = None


class SISOUConfig(list[ISOConfig]):
    """List of ISOConfig objects parsed from a configuration file."""

    def __init__(self, config_path: str) -> None:
        """
        Args:
            config_path (str): Path to the configuration file to parse.
        """
        super().__init__(self._parse_file(config_path))

    @staticmethod
    @cache
    def __get_available_updaters() -> list[Type[GenericUpdater]]:
        return [
            getattr(modules.updaters, updater)
            for updater in dir(modules.updaters)
            if isinstance(getattr(modules.updaters, updater), ABCMeta)
            and issubclass(getattr(modules.updaters, updater), GenericUpdater)
        ]

    @staticmethod
    @cache
    def __get_available_updaters_names() -> list[str]:
        return [updater.__name__ for updater in SISOUConfig.__get_available_updaters()]

    @staticmethod
    def __is_valid_updater(updater_name: str) -> bool:
        return updater_name in SISOUConfig.__get_available_updaters_names()

    @staticmethod
    def __string_to_updater(updater_name: str) -> Type[GenericUpdater]:
        if not SISOUConfig.__is_valid_updater(updater_name):
            raise ValueError(
                f"Invalid updater name: {updater_name}. Available updaters are: {SISOUConfig.__get_available_updaters_names()}"
            )
        return next(
            updater
            for updater in SISOUConfig.__get_available_updaters()
            if updater.__name__ == updater_name
        )

    @staticmethod
    def __load_config(config_path: str) -> dict:
        with open(config_path, "rb") as f:
            return tomllib.load(f)

    def _parse_file(self, config_path: str) -> list[ISOConfig]:
        config_dict = self.__load_config(config_path)
        return self._parse_dir(config_dict)

    def _parse_dir(self, dir_dict: dict, cur_path: str = "") -> list[ISOConfig]:
        if "directory" not in dir_dict:
            raise ValueError("Directory config must have 'directory' key")
        cur_path = os.path.join(cur_path, dir_dict["directory"])
        del dir_dict["directory"]

        isos: list[ISOConfig] = []
        for k, v in dir_dict.items():
            # If the key is disabled, skip it
            if "enabled" not in v or not v["enabled"]:
                del v
                continue
            del v["enabled"]
            if self.__is_valid_updater(k):
                if iso := self._parse_iso(k, v, cur_path):
                    isos.append(iso)
            elif "directory" in v:
                isos += self._parse_dir(v, os.path.join(cur_path))
            else:
                raise ValueError(
                    f"Invalid updater or directory: {k}. Must be either a supported updater or a category with a 'directory' key."
                )
        return isos

    def _parse_iso(
        self, updater_name: str, iso_dict: dict, cur_path: str = ""
    ) -> ISOConfig | None:
        if "name" not in iso_dict:
            raise ValueError(f"'{updater_name}' config must have 'name' key")
        path = ISOPath(iso_dict["name"])
        directory = iso_dict.get("directory")
        if directory:
            path = ISOPath(os.path.join(cur_path, directory, path))
        else:
            path = ISOPath(os.path.join(cur_path, path))
        return ISOConfig(
            iso_path=path,
            updater=self.__string_to_updater(updater_name),
            archs=iso_dict.get("archs"),
            editions=iso_dict.get("editions"),
            langs=iso_dict.get("langs"),
        )
