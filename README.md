# Super ISO Updater

This tool provides a convenient way to check for updates and install the latest versions of various ISO files. It is designed to work with a Ventoy drive and supports a variety of ISOs. This README will guide you on how to use this tool effectively.

## Getting Started

### Prerequisites

- Python 3.10+ installed on your system.

### Installation

1. Clone this repository locally using `git clone https://github.com/FolfyBlue/SuperISOUpdater`

## Usage

To use the `update_isos.py` script, open your terminal or command prompt, navigate to the directory where you placed the script, and follow the steps below:

### Running the script

```sh
python update_isos.py <Ventoy Partition>
```

#### Example on Windows

```sh
python update_isos.py E:
```

#### Example on Linux

```sh
python update_isos.py /run/media/folfy/Ventoy/
```

### Logging

The script generates logs during its execution. You can control the log level using the `-l` or `--log-level` argument when running the script. The available log levels are: DEBUG, INFO, WARNING, ERROR, and CRITICAL. By default, the log level is set to INFO.

To set a specific log level, use the `-l` option followed by the desired log level:

```sh
python update_isos.py <Ventoy Partition> -l DEBUG
```

You can also specify a log file using the `-f` or `--log-file` argument to save the logs to a file instead of displaying them in the console:

```sh
python update_isos.py <Ventoy Partition> -f /path/to/log_file.log
```

## Customization

The `update_isos.py` script uses a configuration file (`config.toml`) to define the ISOs to be updated. You can customize this configuration file to add or remove ISOs from the update process.

To customize the ISOs, open the config.toml file and edit the relevant sections. Each ISO is associated with an updater class (e.g., `Ubuntu`, `MemTest86Plus`, etc.). You can enable or disable ISOs by modifying the corresponding values in the configuration file.

_NOTE: Be cautious when modifying the configuration file, as incorrect changes may cause the script to malfunction._

## Supported ISOs

The tool currently supports the following ISOs:

- Diagnostic Tools
  - Hiren's BootCD PE
  - Memtest86+
  - SystemRescue
- Boot Repair
  - Super Grub 2
- Operating Systems
  - Linux
    - Arch Linux
    - Debian
    - Ubuntu
    - Fedora
    - Linux Mint
    - Manjaro
    - Kali Linux
    - Rocky Linux
    - OpenSUSE
  - Windows
    - Windows 11
    - Windows 10
  - Other
    - N/A
