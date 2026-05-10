import argparse
import logging
import os
import shutil
from abc import ABCMeta
from functools import cache
from itertools import product
from pathlib import Path
from typing import Type

import modules.updaters
from modules.SISOUConfig import SISOUConfig
from modules.updaters import GenericUpdater


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


def setup_logging(log_level: str, log_file: Path | None):
    """Set up logging configurations.

    Args:
        log_level (str): The log level. Valid choices: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        log_file (Path | None): The path to the log file. If None, log to console.

    Raises:
        ValueError: If the log_level is invalid.
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=log_file,
        force=True,
    )

    logging.debug("Logging started")


def run_updater(updater: GenericUpdater):
    """Run a single updater.

    Args:
        updater (GenericUpdater): The updater instance to run.
    """
    installer_for = f"{updater.__class__.__name__}{' ' + updater.edition if updater.edition else ''}{' ' + updater.lang if updater.lang else ''}{' ' + updater.arch if updater.arch else ''}"

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
    except Exception:
        logging.exception(
            f"[{installer_for}] An error occurred while updating. See traceback below."
        )


def create_and_run_updaters(config: SISOUConfig) -> None:
    for iso_config in config:
        edition = iso_config.editions or [None]
        lang = iso_config.langs or [None]
        arch = iso_config.archs or [None]

        for edition, lang, arch in product(edition, lang, arch):
            installer_for = f"{iso_config.updater.__name__}{' ' + edition if edition else ''}{' ' + lang if lang else ''}{' ' + arch if arch else ''}"
            try:
                updater_instance = iso_config.updater(
                    iso_path=iso_config.iso_path,
                    arch=arch,
                    edition=edition,
                    lang=lang,
                )  # type: ignore // We don't pass a mirror_mgr parameter to child classes of GenericUpdater
            except Exception:
                logging.exception(
                    f"[{installer_for}] An error occurred while updating. See traceback below."
                )
                continue
            run_updater(updater_instance)


def main():
    """Main function to run the update process."""
    parser = argparse.ArgumentParser(description="Process a file and set log level")
    parser.add_argument(
        "config_path",
        help="Path to the configuration file or directory containing sisou.toml",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the log level (default: INFO)",
    )
    parser.add_argument(
        "-f", "--log-file", help="Path to the log file (default: log to console)"
    )
    args = parser.parse_args()

    log_file = Path(args.log_file) if args.log_file else None
    setup_logging(args.log_level, log_file)

    config_path = args.config_path

    if os.path.isdir(config_path):
        config_path = os.path.join(config_path, "sisou.toml")

    if not os.path.exists(config_path):
        default_config_path = os.path.join(
            os.path.dirname(__file__), "config", "sisou.toml.default"
        )
        shutil.copyfile(default_config_path, config_path)
        logging.info(
            f"No config file found. A default config file has been created at: {config_path}"
        )
        return

    os.chdir(os.path.dirname(config_path))
    logging.info(f"Using config file: {config_path}")

    config = SISOUConfig(config_path)
    create_and_run_updaters(config)


if __name__ == "__main__":
    main()
