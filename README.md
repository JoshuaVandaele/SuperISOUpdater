# Super ISO Updater

Super ISO Updater is a powerful tool that provides a convenient way to check for updates and install the latest versions of various ISO files. It is specifically designed to work with a Ventoy drive and supports a wide range of ISOs.

## Getting Started

### Prerequisites

- Python 3.12 installed on your system.

### Installation

#### Using pip

1. Open your terminal or command prompt.
2. Install the package using the following command:

```sh
python -m pip install sisou
```

#### Using git

1. Clone this repository locally by running

```sh
git clone https://github.com/JoshuaVandaele/SuperISOUpdater
```

2. Navigate into the newly created directory by running

```sh
cd SuperISOUpdater
```

3. Install the module using the following command:

```sh
python -m pip install .
```

### Updating

To update the package to the latest version, run the following command:

```sh
python -m pip install --upgrade sisou
```

## Usage

To use SISOU, follow these steps:

### Running the script

```sh
sisou <Ventoy Partition>
```

#### Example on Windows

```sh
sisou E:
```

#### Example on Linux

```sh
sisou /run/media/joshua/Ventoy/
```

### Logging

The script generates logs during its execution. You can control the log level using the `-l` or `--log-level` argument when running the script. The available log levels are: DEBUG, INFO, WARNING, ERROR, and CRITICAL. By default, the log level is set to INFO.

To set a specific log level, use the `-l` option followed by the desired log level:

```sh
sisou <Ventoy Partition> -l DEBUG
```

You can also specify a log file using the `-f` or `--log-file` argument to save the logs to a file instead of displaying them in the console:

```sh
sisou <Ventoy Partition> -f /path/to/log_file.log
```

## Customization

The `sisou.py` script uses a configuration file (`config.toml`) to define the ISOs to be updated. You can customize this configuration file to add or remove ISOs from the update process.

To customize the ISOs, open the `config.toml` file and edit the relevant sections. Each ISO is associated with an updater class (e.g., `Ubuntu`, `MemTest86Plus`, etc.). You can enable or disable ISOs by modifying the corresponding values in the configuration file.

_NOTE: Be cautious when modifying the configuration file, as incorrect changes may cause the script to malfunction._

By default, the script uses the `config.toml` file located in the same directory as the Ventoy drive.

You can specify a custom configuration file using the `-c` or `--config-file` argument when running the script:

```sh
sisou <Ventoy Partition> -c /path/to/config.toml
```

## Supported ISOs

The tool currently supports the following ISOs:

- **Diagnostic Tools**
  - Hiren's BootCD PE
  - MemTest86 Plus
  - SystemRescue
  - UltimateBootCD
  - Rescuezilla (editions: "bionic", "focal", "jammy", "noble")
- **Boot Repair**
  - Super Grub 2
- **Disk Utilities**
  - Clonezilla
  - GParted Live
  - ShredOS
  - HDAT2 (editions: "full", "lite", "diskette")
- **Operating Systems**
  - **Linux**
    - Arch Linux
    - Debian (editions: "standard", "cinnamon", "kde", "gnome", "lxde", "lxqt", "mate", "xfce")
    - Ubuntu (editions: "LTS", "interim")
    - Fedora (editions: "Budgie", "Cinnamon", "KDE", "LXDE", "MATE_Compiz", "SoaS", "Sway", "Xfce", "i3")
    - Kali Linux (editions: "installer", "installer-netinst", "installer-purple", "live")
    - Linux Mint (editions: "cinnamon", "mate", "xfce")
    - Manjaro (editions: "plasma", "xfce", "gnome", "cinnamon", "i3")
    - OpenSUSE (editions: "leap", "leap-micro", "jump")
    - OpenSUSE Rolling (editions: "MicroOS-DVD", "Tumbleweed-DVD", "Tumbleweed-NET", "Tumbleweed-GNOME-Live", "Tumbleweed-KDE-Live", "Tumbleweed-XFCE-Live", "Tumbleweed-Rescue-CD")
    - Proxmox (editions: "ve", "mail-gateway", "backup-server")
    - Rocky Linux (editions: "dvd", "boot", "minimal")
    - Tails
    - ChromeOS (editions: "ltc", "ltr", "stable")
  - **Windows**
    - Windows 11 (Multi-edition ISO, Any language)
    - Windows 10 (Multi-edition ISO, Any language)
  - **BSD**
    - TrueNAS (editions: "scale", "core")
  - **Other**
    - FreeDOS (editions: "BonusCD", "FloppyEdition", "FullUSB", "LegacyCD", "LiteUSB", "LiveCD")
    - TempleOS (editions: "Distro", "Lite")

## Contribute

If you have any suggestions, bug reports, or feature requests, feel free to open an issue or submit a pull request. Your contributions are highly appreciated!

## License

This project is licensed under the [GPLv3 License](./LICENSE).

---

Thank you for using Super ISO Updater! If you encounter any issues or need assistance, please don't hesitate to reach out. Happy updating!
