from abc import ABCMeta
import argparse
from functools import cache
import logging
import os
from typing import Type

import modules.updaters
from modules.updaters import GenericUpdater
from modules.utils import logging_critical_exception, parse_config


@cache
def get_available_updaters() -> list[Type[GenericUpdater]]:
    """Get a list of available updaters.

    Returns:
        list[Type[GenericUpdater]]: A list of available updater classes.
    """
    return [
        getattr(modules.updaters, updater)
        for updater in dir(modules.updaters)
        if updater != "GenericUpdater"
        and isinstance(getattr(modules.updaters, updater), ABCMeta)
        and issubclass(getattr(modules.updaters, updater), GenericUpdater)
    ]


def setup_logging(log_level: str, log_file: str | None):
    """Set up logging configurations.

    Args:
        log_level (str): The log level. Valid choices: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        log_file (str | None): The path to the log file. If None, log to console.

    Raises:
        ValueError: If the log_level is invalid.
    """
    numeric_log_level = getattr(logging, log_level, None)

    logging.basicConfig(
        level=numeric_log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=log_file,
    )

    logging.debug("Logging started")


def run_updater(updater: GenericUpdater):
    """Run a single updater.

    Args:
        updater (GenericUpdater): The updater instance to run.
    """
    installer_for = f"{updater.__class__.__name__}{' '+updater.edition if updater.has_edition() else ''}"  # type: ignore

    logging.info(f"[{installer_for}] Checking for updates...")

    try:
        if updater.check_for_updates():
            logging.info(
                f"[{installer_for}] Updates available. Downloading and installing the latest version..."
            )
            updater.install_latest_version()
            logging.info(f"[{installer_for}] Update completed successfully!")
        else:
            logging.info(f"[{installer_for}] No updates available.")
    except:
        logging.exception(
            f"[{installer_for}] An error occurred while updating. See traceback below."
        )


def run_updaters(
    install_path: str, config: dict, updater_list: list[Type[GenericUpdater]]
):
    """Run updaters based on the provided configuration.

    Args:
        install_path (str): The installation path.
        config (dict): The configuration dictionary.
        updater_list (list[Type[GenericUpdater]]): A list of available updater classes.
    """
    for key, value in config.items():
        # If the key's name is the name of an updater, run said updater using the values as argument, otherwise assume it's a folder's name
        if key in [updater.__name__ for updater in updater_list]:
            updater_class = next(
                updater for updater in updater_list if updater.__name__ == key
            )

            updaters: list[GenericUpdater] = []

            params: list[dict] = [{}]

            editions = value.get("editions", [])
            langs = value.get("langs", [])

            if editions and langs:
                params = [
                    {"edition": edition, "lang": lang}
                    for edition in editions
                    for lang in langs
                ]
            elif editions:
                params = [{"edition": edition} for edition in editions]
            elif langs:
                params = [{"lang": lang} for lang in langs]

            for param in params:
                try:
                    updaters.append(updater_class(install_path, **param))
                except Exception:
                    installer_for = f"{key} {param}"
                    logging.exception(
                        f"[{installer_for}] An error occurred while trying to add the installer. See traceback below."
                    )
            # Run updater(s)
            for updater in updaters:
                run_updater(updater)

        else:
            run_updaters(os.path.join(install_path, key), value, updater_list)


def main():
    """Main function to run the update process."""
    parser = argparse.ArgumentParser(description="Process a file and set log level")

    # Add the positional argument for the file path
    parser.add_argument("ventoy_path", help="Path to the Ventoy drive")

    # Add the optional argument for log level
    parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the log level (default: INFO)",
    )

    # Add the optional argument for log file
    parser.add_argument(
        "-f", "--log-file", help="Path to the log file (default: log to console)"
    )

    # Add the optional argument for config file
    parser.add_argument(
        "-c", "--config-file", help="Path to the config file (default: config.toml)"
    )

    args = parser.parse_args()

    setup_logging(args.log_level, args.log_file)

    config_file = args.config_file
    if not config_file:
        logging.info(
            "No config file specified. Trying to find config.toml in the current directory..."
        )
        config_file = os.path.join(os.getcwd(), "config.toml")

        if not os.path.isfile(config_file):
            logging.info(
                "No config file specified. Trying to find config.toml in the ventoy drive..."
            )
            config_file = os.path.join(args.ventoy_path, "config.toml")

            if not os.path.isfile(config_file):
                logging.info(
                    "No config.toml found in the ventoy drive. Generating one from config.toml.default..."
                )
                with open(
                    os.path.join(
                        os.path.dirname(__file__), "config", "config.toml.default"
                    )
                ) as default_config_file:
                    with open(config_file, "w") as new_config_file:
                        new_config_file.write(default_config_file.read())
                logging.info(
                    "Generated config.toml in the ventoy drive. Please edit it to your liking and run sisou again."
                )
                return

    config = parse_config(config_file)
    if not config:
        raise ValueError("Configuration file could not be parsed or is empty")

    available_updaters: list[Type[GenericUpdater]] = get_available_updaters()

    run_updaters(args.ventoy_path, config, available_updaters)

    logging.debug("Finished execution")


if __name__ == "__main__":
    main()
