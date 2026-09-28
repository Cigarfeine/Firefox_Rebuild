# firefox-rebuild

[![PyPI version](https://img.shields.io/pypi/v/firefox-rebuild?style=flat-square&color=0066CC)](https://pypi.org/project/firefox-rebuild/)
[![Python versions](https://img.shields.io/pypi/pyversions/firefox-rebuild?style=flat-square)](https://pypi.org/project/firefox-rebuild/)
[![License](https://img.shields.io/github/license/Cigarfeine/Firefox_Rebuild?style=flat-square)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/Cigarfeine/Firefox_Rebuild/ci.yml?style=flat-square)](https://github.com/Cigarfeine/Firefox_Rebuild/actions)
[![Tests](https://img.shields.io/badge/tests-10%20passed-brightgreen?style=flat-square)](#)

> A friendly Firefox installer for lab environments — because manually updating 52 machines one by one is nobody's idea of a good time.

---

## Why This Exists

Our college lab has **52 systems**. Every Firefox update meant someone walking machine-to-machine, running commands, waiting for downloads, verifying it worked... you get the picture.

Most lab PCs have restricted environments **without `pip` or `git`**.

This tool is built with **zero external dependencies** using pure standard Python. You can just download the project archive and run a single command!

## Features

| Feature | Description |
|---------|-------------|
| 🚀 **Zero Dependencies** | Built using pure Python standard library — works without `pip` or `git` |
| 📦 **Direct from Mozilla** | No repo delays, no snap/flatpak drama |
| 🧹 **Clean install** | Removes old versions first, no cruft left behind |
| 🖥️ **Desktop integration** | Shows up in app menu with icons and actions |
| 🔄 **Self-updating Firefox** | Installed Firefox handles its own updates; re-run for latest build |
| 🧪 **Dry-run mode** | See what would happen before committing |
| 🎨 **Pretty output** | Clean ANSI banners, live download progress, and formatted tables |

---

## ⚡ Quick Start (No pip or git required)

### 1. Download & Run on Lab Machines

Download the ZIP from GitHub, extract it, and run the installer:

```bash
unzip Firefox_Rebuild-main.zip
cd Firefox_Rebuild-main
sudo ./install.sh
```

*(Alternatively: `sudo python3 run.py`)*

### 2. One-Liner (Over LAN / Direct)

```bash
curl -sSL https://raw.githubusercontent.com/Cigarfeine/Firefox_Rebuild/main/install.sh | sudo bash
```

### 3. Optional: Install from PyPI

```bash
pip install firefox-rebuild
sudo firefox-rebuild install
```

---

## Usage & Commands

```bash
# Install or update Firefox (needs sudo)
sudo ./install.sh
# or: sudo python3 run.py install

# Preview what would happen (no changes made)
./install.sh --dry-run
# or: python3 run.py install --dry-run

# Skip confirmation prompt
sudo ./install.sh -y

# Check what's currently installed
./install.sh status
# or: python3 run.py status

# See the installed version
./install.sh version
# or: python3 run.py version

# Remove the manual installation
sudo ./install.sh uninstall
# or: sudo python3 run.py uninstall
```

---

## What It Actually Does

1. Removes old system Firefox packages (`apt-get remove firefox`)
2. Cleans up `/opt/firefox` if an old version exists
3. Downloads the latest official Firefox build directly from Mozilla CDN
4. Extracts to `/opt/firefox`
5. Creates `/usr/bin/firefox` symlink
6. Creates `/usr/share/applications/firefox.desktop` with application menu integration
7. Verifies the installation

---

## Requirements

- **Debian / Ubuntu-based Linux** (tested on Ubuntu 20.04, 22.04, 24.04, Debian 11/12)
- **Python 3.9+** (Standard installation, no external pip packages required)
- **sudo** privileges for installation
- **Internet connection** (downloads ~80-100 MB directly from Mozilla)

---

## Development & Testing

```bash
# Run test suite with built-in standard library unittest:
PYTHONPATH=src python3 -m unittest discover tests

# Or with pytest:
pytest tests -v
```