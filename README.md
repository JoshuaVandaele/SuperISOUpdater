# Super ISO Updater

> [!WARNING]  
> This branch is still a work in progress. As such, not all listed features may be available yet.

Super ISO Updater (SISOU) is a powerful tool that provides a convenient way to check for updates and install the latest versions of various ISO files. It is primarily meant to be used with a Ventoy drive and supports a wide range of ISOs.

## Features

- **Automatic ISO Updates:** Automatically check for and downloads the latest ISO versions from official sources, always using the fastest available mirror.
- **Checksum & Signature Verification:** Verifies the integrity of every downloaded file, ensuring nothing has been corrupted or tempered with.
- **Flexible Organization & Configuration:** Organize your ISOs exactly the way you want on your drive and manage them effortlessly. Enable, disable, or add new ones through the configuration file. (We recommend using [TreeView Mode](https://www.ventoy.net/en/doc_treeview.html) in Ventoy.)
- **Wide ISO Support:** Compatible with a broad range of operating systems, utilities, and diagnostic tools. (See [Supported ISOs](#supported-isos))

## Getting Started

### Prerequisites

- Python 3.12 installed on your system.
- GnuPG for signature verification. (Optional)

### Installation

Pick whichever method works best for you:

#### pip _(recommended for most users)_

```sh
python -m pip install sisou
```

#### pipx

```sh
pipx install sisou
```

#### From source

```sh
git clone https://github.com/JoshuaVandaele/SuperISOUpdater
cd SuperISOUpdater
python -m pip install .
```

### Updating

#### pip

```sh
python -m pip install --upgrade sisou
```

#### pipx

```sh
pipx upgrade sisou
```

#### From source

```sh
cd SuperISOUpdater
git pull
python -m pip install .
```

## Usage

To use SISOU, follow these steps:

### Running SISOU

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

SISOU generates logs during its execution. You can control the log level using the `-l` or `--log-level` argument. The available log levels are: DEBUG, INFO, WARNING, ERROR, and CRITICAL. By default, the log level is set to INFO.

To set a specific log level, use the `-l` option followed by the desired log level:

```sh
sisou <Ventoy Partition> -l DEBUG
```

You can also specify a log file using the `-f` or `--log-file` argument to save the logs to a file instead of displaying them in the console:

```sh
sisou <Ventoy Partition> -f /path/to/log_file.log
```

## Customization

SISOU is configured through a `config.toml` file, where you can control which ISOs get updated and how: toggling them on or off, and choosing your preferred editions, languages, and architectures.

By default, SISOU looks for `config.toml` in the same directory as your Ventoy drive. You can point it to a different file with the `-c` / `--config-file` argument:

```sh
sisou <Ventoy Partition> -c /path/to/config.toml
```

> [!TIP]
> No config file yet? No problem, one will be created for you automatically on the first run.

## Supported ISOs

The tool currently supports the following ISOs:

- **Diagnostic Tools**
  - ✅ Hiren's BootCD PE
  - ✅ MemTest86 Plus
    - Architectures: x86_64, i586
  - ✅ SystemRescue
  - ✅ UltimateBootCD
  - ✅ Rescuezilla
    - Editions: bionic, focal, jammy, noble
    - Architectures: 64bit, 32bit
- **Disk Utilities**
  - ✅ Clonezilla
  - ✅ GParted Live
  - ✅ ShredOS
    - Architectures: x86-64, i586
  - ✅ HDAT2
    - Editions: full, lite, diskette
- **Operating Systems**
  - **Linux**
    - ✅ Alpine Linux
      - Editions: standard
      - Architectures: aarch64, armv7, loongarch64, ppc64le, riscv64, s390x, x86, x86_64
    - ✅ Arch Linux
    - ✅ Debian
      - Architectures: amd64, arm64, armhf, ppc64el, riscv64, s390x
    - ✅ Ubuntu
      - Editions: desktop, live-server
    - ✅ Fedora
      - Editions: Budgie, Cinnamon, KDE, LXDE, MATE_Compiz, SoaS, Sway, Xfce, i3
      - Architectures: x86_64, aarch64
    - 🔳 Kali Linux
      - Editions: installer, installer-netinst, installer-purple, live
      - Architectures: amd64, arm64
    - ✅ Linux Mint
      - Editions: cinnamon, mate, xfce
    - 🔳 Manjaro
      - Editions: plasma, xfce, gnome, cinnamon, i3"
      - Architectures: amd64, ARM
    - 🔳 OpenSUSE
      - Editions: leap, leap-micro, jump
      - Architectures: x86_64, aarch64, s390x, i686, ppc64le
    - 🔳 OpenSUSE Rolling
      - Editions: MicroOS-DVD, Tumbleweed-DVD, Tumbleweed-NET, Tumbleweed-GNOME-Live, Tumbleweed-KDE-Live, Tumbleweed-XFCE-Live, Tumbleweed-Rescue-CD
    - 🔳 OPNsense
      - Editions: dvd, nano, serial, vga
    - ✅ Proxmox
      - Editions: ve, mail-gateway, backup-server
    - 🔳 Rocky Linux
      - Editions: dvd, boot, minimal
      - Architectures: x86_64, aarch64, ppc64le, s390x, riscv64
    - 🔳 Rocky Linux Live
      - Editions: KDE, Workstation, Workstation Lite
      - Architectures: x86_64, aarch64
    - ✅ TrueNAS
    - ✅ Tails
  - **Windows**
    - ✅ Windows 11 (Multi-edition ISO, Any language)
      - Architectures: x64, arm64
    - ✅ Windows 10 (Multi-edition ISO, Any language)
  - **BSD**

## Contributing

If you have any suggestions, bug reports, or feature requests, feel free to open an issue or submit a pull request. Your contributions are highly appreciated!

## License

This project is licensed under the [GPL-2.0-or-later](./LICENSE) license.

---

Thank you for using Super ISO Updater!

<img src="assets/sisou.svg" alt="Super ISO Updater" width="200" />
