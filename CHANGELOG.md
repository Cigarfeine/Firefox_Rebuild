# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-19

### Added
- Initial release of firefox-rebuild
- `install` command with dry-run support
- `status` command to check installation state
- `version` command to show installed Firefox version
- `uninstall` command to remove manual installation
- Beautiful terminal UI with Rich (banners, progress bars, tables)
- Cross-platform support (Linux for real installs, Windows for dry-run)
- Direct download from Mozilla CDN
- Proper desktop entry with icons and actions
- Comprehensive test suite (7 tests passing)
- CI/CD with GitHub Actions (lint, type-check, tests)
- Type hints throughout codebase

### Features
- Downloads latest Firefox directly from Mozilla
- Cleans up old installations (apt packages + manual)
- Creates `/opt/firefox` with symlink at `/usr/bin/firefox`
- Generates `.desktop` file for application menu integration
- Dry-run mode for safe testing
- Human-friendly output messages

---

**Full history:** https://github.com/Cigarfeine/Firefox_Rebuild/commits/main