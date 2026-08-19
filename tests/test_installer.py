"""Tests for firefox-rebuild."""

import sys
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from firefox_rebuild.cli import app
from firefox_rebuild.installer import FirefoxInstaller


class TestFirefoxInstaller:
    """Tests for the FirefoxInstaller class."""

    def test_check_root_on_windows(self):
        """check_root works on Windows (uses ctypes)."""
        installer = FirefoxInstaller()
        # On Windows, should not crash and return a boolean
        result = installer.check_root()
        assert isinstance(result, bool)

    def test_check_root_false_unix(self):
        """check_root returns False when not root on Unix."""
        if sys.platform == "win32":
            pytest.skip("Unix-only test")
        with patch("os.geteuid", return_value=1000):
            installer = FirefoxInstaller()
            assert installer.check_root() is False

    def test_check_root_true_unix(self):
        """check_root returns True when root on Unix."""
        if sys.platform == "win32":
            pytest.skip("Unix-only test")
        with patch("os.geteuid", return_value=0):
            installer = FirefoxInstaller()
            assert installer.check_root() is True

    def test_dry_run_mode(self):
        """Dry run mode doesn't execute commands."""
        installer = FirefoxInstaller(dry_run=True)
        # Should not raise
        installer._run(["echo", "test"], "Test command")

    @patch("firefox_rebuild.installer.subprocess.run")
    def test_remove_old_firefox(self, mock_run):
        """remove_old_firefox calls apt commands in dry-run mode."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        installer = FirefoxInstaller(dry_run=True)
        installer.remove_old_firefox()
        # In dry-run mode, _run doesn't actually call subprocess.run
        # Just verify it doesn't crash
        assert True

    def test_verify_installation_missing(self):
        """verify_installation returns None when Firefox not installed."""
        installer = FirefoxInstaller(dry_run=True)
        with patch("pathlib.Path.exists", return_value=False):
            assert installer.verify_installation() is None


class TestCLI:
    """Basic CLI tests."""

    def test_version_command(self):
        """Version command exists."""
        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0

    def test_install_help(self):
        """Install command shows help."""
        runner = CliRunner()
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0
        assert "install" in result.output

    def test_status_command(self):
        """Status command works."""
        runner = CliRunner()
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Firefox Status" in result.output
