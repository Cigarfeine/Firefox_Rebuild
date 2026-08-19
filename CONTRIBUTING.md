# Contributing to firefox-rebuild

Thanks for considering a contribution! This project was built for a college lab with 52 machines, but aims to be useful for anyone managing Firefox on Debian/Ubuntu systems.

## Ways to Contribute

- **Bug reports** — Found something broken? Open an issue with steps to reproduce.
- **Feature requests** — Have an idea? Open an issue to discuss it first.
- **Code changes** — Submit a PR with tests.
- **Documentation** — Fix typos, improve README, add examples.
- **Testing** — Test on different distros/versions and report results.

## Development Setup

```bash
# Clone and install in dev mode
git clone https://github.com/Cigarfeine/Firefox_Rebuild
cd Firefox_Rebuild
pip install -e ".[dev]"

# Run tests
pytest tests -v

# Lint & format
ruff check src tests
ruff format src tests

# Type check
mypy src
```

## Code Style

- **Python 3.9+** with type hints
- **ruff** for linting/formatting (line length: 100)
- **mypy** for type checking (strict mode)
- **pytest** for testing
- **Rich** for terminal UI

## Pull Request Process

1. Fork the repo and create a branch from `main`
2. Make your changes with tests
3. Run the full test suite: `pytest tests -v && ruff check src tests && mypy src`
4. Update CHANGELOG.md if user-facing
5. Open a PR with a clear description

## Testing on Different Systems

Since this targets lab environments, testing on various distros helps:

| Distro | Version | Status |
|--------|---------|--------|
| Ubuntu | 20.04 | ✅ Tested |
| Ubuntu | 22.04 | ✅ Tested |
| Ubuntu | 24.04 | ✅ Tested |
| Debian | 11 | 🔄 Untested |
| Debian | 12 | 🔄 Untested |
| Linux Mint | 21 | 🔄 Untested |

If you test on an unlisted system, please report results in an issue!

## Code of Conduct

Be respectful. This is a small project maintained by one person in their spare time. Constructive feedback welcome; entitlement not.

## Questions?

Open a [discussion](https://github.com/Cigarfeine/Firefox_Rebuild/discussions) or [issue](https://github.com/Cigarfeine/Firefox_Rebuild/issues).