# firefox-rebuild

A friendly Firefox installer for lab environments — because manually updating 52 machines one by one is nobody's idea of a good time.

## The Story

Our college lab has 52 systems. Every time Firefox needed an update, someone had to go machine to machine, run commands, wait for downloads, verify it worked... you get the picture. This tool was born from that frustration.

It grabs the latest Firefox directly from Mozilla, installs it cleanly to `/opt/firefox`, sets up the symlink and desktop entry, and gets out of your way.

## Features

- **Downloads straight from Mozilla** — no repo delays, no snap/flatpak drama
- **Clean installation** — removes old versions first, no cruft left behind
- **Proper desktop integration** — shows up in your app menu with icons and actions
- **Self-updating Firefox** — the installed Firefox handles its own updates; re-run this when you want the very latest build
- **Dry-run mode** — see what would happen before committing
- **Pretty output** — because life's too short for ugly terminal tools

## Installation

```bash
# Install the tool itself
pip install firefox-rebuild

# Or install from source
git clone https://github.com/Cigarfeine/Firefox_Rebuild
cd Firefox_Rebuild
pip install -e .
```

## Usage

```bash
# Install/update Firefox (needs sudo)
sudo firefox-rebuild install

# See what would happen without making changes
firefox-rebuild install --dry-run

# Skip the confirmation prompt
sudo firefox-rebuild install --yes

# Check what's currently installed
firefox-rebuild status

# See the installed version
firefox-rebuild version

# Remove the manual installation
sudo firefox-rebuild uninstall
```

## What It Does

1. Removes the system Firefox package (`apt remove firefox`)
2. Cleans up `/opt/firefox` if it exists
3. Downloads the latest Firefox tarball from Mozilla
4. Extracts to `/opt/firefox`
5. Creates `/usr/bin/firefox` symlink
6. Creates `/usr/share/applications/firefox.desktop` with proper icons and actions
7. Verifies the installation

## Requirements

- Debian/Ubuntu-based system (tested on Ubuntu 20.04, 22.04, 24.04)
- Python 3.9+
- `sudo` privileges for installation
- Internet connection (downloads ~80-100 MB)

## Why Not Just Use apt/snap/flatpak?

| Method | Problem |
|--------|---------|
| `apt` | Often months behind; ESR only on some releases |
| `snap` | Slow startup; sandbox issues in lab environments |
| `flatpak` | Extra layer; not always available by default |
| **firefox-rebuild** | Latest stable, direct from Mozilla, native performance |

## License

MIT — do whatever you want with it.

## Contributing

Found a bug? Have an idea? Open an issue or PR. This was built for a specific lab setup but tries to be generally useful.

---

*Built with ☕ and mild frustration by [Cigarfeine](https://github.com/Cigarfeine)*