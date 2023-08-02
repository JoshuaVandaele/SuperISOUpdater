import argparse
import logging
import os
from typing import Type

from modules.updaters import *
from modules.utils import logging_critical_exception, parse_config


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

            params: list[dict] = []
            # Parse parameters and create updater instances
            if "editions" in value:
                for edition in value["editions"]:
                    params.append({"edition": edition})
            else:
                params.append({})
            if "lang" in value:
                param_len = len(params)
                params += params
                for i in range(param_len):
                    for lang in value["lang"]:
                        params[i]["lang"] = lang
                        params[i + param_len]["lang"] = lang

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


def main(ventoy_path: str, log_level: str, log_file: str | None):
    """Main function to run the update process.

    Args:
        ventoy_path (str): Path to the Ventoy drive.
        log_level (str): The log level. Valid choices: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        log_file (str | None): The path to the log file. If None, log to console.
    """
    setup_logging(log_level, log_file)

    config = parse_config("config.toml")
    if not config:
        raise ValueError("Configuration file could not be parsed or is empty")

    available_updaters: list[Type[GenericUpdater]] = [
        # Diagnostic Tools
        HirensBootCDPE,
        MemTest86Plus,
        SystemRescue,
        # Boot Repair
        SuperGrub2,
        # Operating Systems
        ArchLinux,
        Debian,
        Ubuntu,
        Fedora,
        LinuxMint,
        Manjaro,
        KaliLinux,
        RockyLinux,
        OpenSUSE,
        Windows11,
        Windows10,
    ]

    run_updaters(ventoy_path, config, available_updaters)

    logging.debug("Finished execution")


if __name__ == "__main__":
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

    args = parser.parse_args()

    try:
        main(args.ventoy_path, args.log_level, args.log_file)
    except Exception:
        logging_critical_exception(
            "An error occurred while executing the main function! See traceback below for a detailed traceback."
        )
