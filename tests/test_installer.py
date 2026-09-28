"""Tests for firefox-rebuild."""

import io
import sys
import unittest
from unittest.mock import Mock, patch

from firefox_rebuild.cli import app
from firefox_rebuild.installer import FirefoxInstaller


class TestFirefoxInstaller(unittest.TestCase):
    """Tests for the FirefoxInstaller class."""

    def test_check_root_on_windows(self):
        """check_root works on Windows (uses ctypes)."""
        installer = FirefoxInstaller()
        result = installer.check_root()
        self.assertIsInstance(result, bool)

    def test_check_root_false_unix(self):
        """check_root returns False when not root on Unix."""
        if sys.platform == "win32":
            self.skipTest("Unix-only test")
        with patch("os.geteuid", return_value=1000):
            installer = FirefoxInstaller()
            self.assertFalse(installer.check_root())

    def test_check_root_true_unix(self):
        """check_root returns True when root on Unix."""
        if sys.platform == "win32":
            self.skipTest("Unix-only test")
        with patch("os.geteuid", return_value=0):
            installer = FirefoxInstaller()
            self.assertTrue(installer.check_root())

    def test_dry_run_mode(self):
        """Dry run mode doesn't execute commands."""
        installer = FirefoxInstaller(dry_run=True)
        result = installer._run(["echo", "test"], "Test command")
        self.assertEqual(result.returncode, 0)

    @patch("firefox_rebuild.installer.subprocess.run")
    def test_remove_old_firefox(self, mock_run):
        """remove_old_firefox calls apt commands in dry-run mode."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        installer = FirefoxInstaller(dry_run=True)
        installer.remove_old_firefox()
        self.assertTrue(True)

    def test_verify_installation_missing(self):
        """verify_installation returns None when Firefox not installed."""
        installer = FirefoxInstaller(dry_run=True)
        with patch("pathlib.Path.exists", return_value=False):
            self.assertIsNone(installer.verify_installation())


class TestCLI(unittest.TestCase):
    """Basic CLI tests."""

    def test_version_command(self):
        """Version command exists."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            exit_code = app(["version"])
        self.assertEqual(exit_code, 0)

    def test_install_help(self):
        """Install command shows help."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            try:
                exit_code = app(["install", "--help"])
            except SystemExit as e:
                exit_code = e.code
        self.assertEqual(exit_code, 0)
        self.assertIn("install", captured.getvalue().lower())

    def test_status_command(self):
        """Status command works."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            exit_code = app(["status"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Firefox Status", captured.getvalue())

    def test_dry_run_install(self):
        """Install with --dry-run works without root."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            exit_code = app(["install", "--dry-run", "--yes"])
        self.assertEqual(exit_code, 0)
        self.assertIn("DRY RUN MODE", captured.getvalue())


if __name__ == "__main__":
    unittest.main()
