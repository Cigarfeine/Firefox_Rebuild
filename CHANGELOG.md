# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-09-28

### Added
- Zero-dependency support using pure Python standard library (`urllib.request`, `argparse`, ANSI formatting).
- Root `install.sh` and `run.py` launcher scripts for single-command lab deployment.
- Package `__main__.py` entry point (`python3 -m firefox_rebuild`).
- Standard library `unittest` test runner compatibility.

### Changed
- Removed required third-party runtime dependencies (`rich`, `typer`, `httpx`, `psutil`) so the program runs out-of-the-box in restricted lab environments without `pip`.

---

## [1.0.0] - 2026-08-19

### Added
- Initial release of firefox-rebuild
- `install` command with dry-run support
- `status` command to check installation state
- `version` command to show installed Firefox version
- `uninstall` command to remove manual installation
- Cross-platform support (Linux for real installs, Windows for dry-run)
- Direct download from Mozilla CDN
- Proper desktop entry with icons and actions
- CI/CD with GitHub Actions

---

**Full history:** https://github.com/Cigarfeine/Firefox_Rebuild/commits/main