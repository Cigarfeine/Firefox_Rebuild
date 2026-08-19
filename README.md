# firefox-rebuild

[![PyPI version](https://img.shields.io/pypi/v/firefox-rebuild?style=flat-square&color=0066CC)](https://pypi.org/project/firefox-rebuild/)
[![Python versions](https://img.shields.io/pypi/pyversions/firefox-rebuild?style=flat-square)](https://pypi.org/project/firefox-rebuild/)
[![License](https://img.shields.io/github/license/Cigarfeine/Firefox_Rebuild?style=flat-square)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/Cigarfeine/Firefox_Rebuild/ci.yml?style=flat-square)](https://github.com/Cigarfeine/Firefox_Rebuild/actions)
[![Tests](https://img.shields.io/badge/tests-7%20passed-brightgreen?style=flat-square)](#)

> A friendly Firefox installer for lab environments — because manually updating 52 machines one by one is nobody's idea of a good time.

---

## Why This Exists

Our college lab has **52 systems**. Every Firefox update meant someone walking machine-to-machine, running commands, waiting for downloads, verifying it worked... you get the picture.

This tool was born from that frustration. It grabs the latest Firefox **directly from Mozilla**, installs it cleanly to `/opt/firefox`, sets up the symlink and desktop entry, and gets out of your way.

## Features

| Feature | Description |
|---------|-------------|
| 📦 **Direct from Mozilla** | No repo delays, no snap/flatpak drama |
| 🧹 **Clean install** | Removes old versions first, no cruft left behind |
| 🖥️ **Desktop integration** | Shows up in app menu with icons and actions |
| 🔄 **Self-updating Firefox** | Installed Firefox handles its own updates; re-run for latest build |
| 🧪 **Dry-run mode** | See what would happen before committing |
| 🎨 **Pretty output** | Because life's too short for ugly terminal tools |

## Quick Demo

```bash
$ firefox-rebuild install --dry-run

+--------------------------------------------------------------+
|                                                              |
|    ___ _            _     _ _  ___ _   _ ____                |
|   / _ \ |__   __ _| |__ | | |/ _ \ | | | |  _ \              |
|  | | | | '_ \ / _` | '_ \| | | | | | | | | |_) |             |
|  | |_| | |_) | (_| | |_) | | | |_| | |_| |  _ <              |
|   \___/|_.__/ \__,_|_.__/|_|_|\___/ \__,_|_| \_\             |
|                                                              |
|           rebuild — lab-friendly Firefox installer          |
+--------------------------------------------------------------+

[TEST] DRY RUN MODE — no changes will be made

[!] This tool is designed for Debian/Ubuntu-based systems.
It might work on others, but no promises.


firefox-rebuild — Installing Firefox

DRY RUN: Removing old Firefox packages
  -> apt-get remove -y firefox firefox-locale-en
DRY RUN: Cleaning up unused packages
  -> apt-get autoremove -y
DRY RUN: Would download Firefox to /tmp/xxx.tar.xz
DRY RUN: Would extract to /opt/firefox
DRY RUN: Would create symlink /usr/bin/firefox -> /opt/firefox/firefox
DRY RUN: Would write desktop entry to /usr/share/applications/firefox.desktop

+--------------------------------------------------------------+
|                                                              |
|     ____  _   _ ____    ___ ____ ____  ____                  |
|    / ___|| | | |  _ \  |_ _/ ___|  _ \|  _ \                 |
|    \___ \| | | | |_) |  | | |   | |_) | | | |                |
|     ___) | |_| |  _ <   | | |___|  _ <| |_| |                |
|    |____/ \___/|_| \_\ |___\____|_| \_\____/                 |
|                                                              |
+--------------------------------------------------------------+


Firefox DRY RUN is ready to go (fox)

  Install location    /opt/firefox
  Command             firefox (via /usr/bin/firefox)
  Desktop entry       /usr/share/applications/firefox.desktop
  Version             DRY RUN
```

## Installation

```bash
# From PyPI (recommended)
pip install firefox-rebuild

# From source
git clone https://github.com/Cigarfeine/Firefox_Rebuild
cd Firefox_Rebuild
pip install -e .
```

## Usage

```bash
# Install/update Firefox (needs sudo)
sudo firefox-rebuild install

# Preview what would happen (no changes)
firefox-rebuild install --dry-run

# Skip confirmation prompt
sudo firefox-rebuild install --yes

# Check what's currently installed
firefox-rebuild status

# See the installed version
firefox-rebuild version

# Remove the manual installation
sudo firefox-rebuild uninstall
```

## What It Actually Does

1. Removes the system Firefox package (`apt remove firefox`)
2. Cleans up `/opt/firefox` if it exists
3. Downloads the latest Firefox tarball from Mozilla (~80-100 MB)
4. Extracts to `/opt/firefox`
5. Creates `/usr/bin/firefox` symlink
6. Creates `/usr/share/applications/firefox.desktop` with proper icons and actions
7. Verifies the installation

## Requirements

- **Debian/Ubuntu-based** (tested on Ubuntu 20.04, 22.04, 24.04)
- **Python 3.9+**
- **sudo** privileges for installation
- **Internet connection** (downloads ~80-100 MB)

## Why Not apt / snap / flatpak?

| Method | Problem |
|--------|---------|
| `apt` | Often months behind; ESR only on some releases |
| `snap` | Slow startup; sandbox issues in lab environments |
| `flatpak` | Extra layer; not always available by default |
| **firefox-rebuild** | Latest stable, direct from Mozilla, native performance |

## Project Health

- ✅ **Tests passing** (7 passed, 2 skipped on Windows)
- ✅ **Linting clean** (ruff, mypy configured)
- ✅ **CI/CD** (GitHub Actions on push/PR)
- ✅ **Type hints** throughout
- ✅ **Cross-platform** (Linux install, Windows dry-run)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests -v

# Lint
ruff check src tests
ruff format --check src tests

# Type check
mypy src

# Build package
python -m build
```

## License

MIT — do whatever you want with it.

## Contributing

Found a bug? Have an idea? Open an issue or PR. This was built for a specific lab setup but tries to be generally useful.

---

<p align="center">
  Built with ☕ and mild frustration by <a href="https://github.com/Cigarfeine">Cigarfeine</a>
</p>

<p align="center">
  <a href="https://github.com/Cigarfeine/Firefox_Rebuild/issues">Report Bug</a> •
  <a href="https://github.com/Cigarfeine/Firefox_Rebuild/issues">Request Feature</a> •
  <a href="https://github.com/Cigarfeine/Firefox_Rebuild/blob/main/CHANGELOG.md">Changelog</a>
</p>