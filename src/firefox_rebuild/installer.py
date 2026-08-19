"""
Core installation logic — the parts that actually do the work.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import httpx
from rich.console import Console

console = Console()

FIREFOX_DOWNLOAD_URL = "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"
INSTALL_DIR = Path("/opt/firefox")
SYMLINK_PATH = Path("/usr/bin/firefox")
DESKTOP_ENTRY_PATH = Path("/usr/share/applications/firefox.desktop")


class FirefoxInstaller:
    """Handles the actual Firefox installation process."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.console = console

    def _run(self, cmd: list[str], description: str) -> subprocess.CompletedProcess:
        """Run a command with nice output."""
        if self.dry_run:
            self.console.print(f"[dim]DRY RUN:[/dim] {description}")
            self.console.print(f"[dim]  ->[/dim] {' '.join(cmd)}")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        self.console.print(f"[cyan]>[/cyan] {description}")
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red][X][/red] {description} failed")
            self.console.print(f"[red]  {e.stderr.strip()}[/red]")
            raise

    def check_root(self) -> bool:
        """Check if we're running as root/admin."""
        if hasattr(os, 'geteuid'):
            return os.geteuid() == 0
        # Windows: check if running as admin
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def remove_old_firefox(self) -> None:
        """Remove any existing Firefox installations."""
        self._run(
            ["apt-get", "remove", "-y", "firefox", "firefox-locale-en"],
            "Removing old Firefox packages",
        )
        self._run(["apt-get", "autoremove", "-y"], "Cleaning up unused packages")

        if INSTALL_DIR.exists():
            if self.dry_run:
                self.console.print(f"[dim]DRY RUN:[/dim] Would remove {INSTALL_DIR}")
            else:
                shutil.rmtree(INSTALL_DIR, ignore_errors=True)
                self.console.print(f"[green][OK][/green] Removed {INSTALL_DIR}")

    def download_firefox(self, progress_callback=None) -> Path:
        """Download the latest Firefox tarball."""
        with tempfile.NamedTemporaryFile(suffix=".tar.xz", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        if self.dry_run:
            self.console.print(f"[dim]DRY RUN:[/dim] Would download Firefox to {tmp_path}")
            return tmp_path

        self.console.print("[cyan]>[/cyan] Downloading latest Firefox...")

        with httpx.stream("GET", FIREFOX_DOWNLOAD_URL, follow_redirects=True) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(tmp_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total > 0:
                        progress_callback(downloaded, total)

        self.console.print(f"[green][OK][/green] Downloaded {tmp_path.stat().st_size / 1024 / 1024:.1f} MB")
        return tmp_path

    def extract_firefox(self, tarball: Path) -> None:
        """Extract Firefox to /opt/firefox."""
        if self.dry_run:
            self.console.print(f"[dim]DRY RUN:[/dim] Would extract to {INSTALL_DIR}")
            return

        self.console.print("[cyan]>[/cyan] Extracting Firefox...")

        # Ensure parent directory exists
        INSTALL_DIR.parent.mkdir(parents=True, exist_ok=True)

        # Remove old installation if exists
        if INSTALL_DIR.exists():
            shutil.rmtree(INSTALL_DIR)

        self._run(
            ["tar", "-xJf", str(tarball), "-C", str(INSTALL_DIR.parent)],
            f"Extracting to {INSTALL_DIR}",
        )

        self.console.print(f"[green][OK][/green] Extracted to {INSTALL_DIR}")

    def create_symlink(self) -> None:
        """Create /usr/bin/firefox symlink."""
        if self.dry_run:
            self.console.print(f"[dim]DRY RUN:[/dim] Would create symlink {SYMLINK_PATH} -> {INSTALL_DIR}/firefox")
            return

        self._run(
            ["ln", "-sf", str(INSTALL_DIR / "firefox"), str(SYMLINK_PATH)],
            f"Creating symlink {SYMLINK_PATH}",
        )
        self.console.print(f"[green][OK][/green] Symlink created")

    def create_desktop_entry(self) -> None:
        """Create .desktop file for application menu."""
        desktop_content = f"""[Desktop Entry]
Version=1.0
Name=Firefox
GenericName=Web Browser
Comment=Browse the World Wide Web
Exec={INSTALL_DIR}/firefox %u
Terminal=false
Icon={INSTALL_DIR}/browser/chrome/icons/default/default128.png
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
Actions=new-window;new-private-window;

[Desktop Action new-window]
Name=New Window
Exec={INSTALL_DIR}/firefox --new-window

[Desktop Action new-private-window]
Name=New Private Window
Exec={INSTALL_DIR}/firefox --private-window
"""

        if self.dry_run:
            self.console.print(f"[dim]DRY RUN:[/dim] Would write desktop entry to {DESKTOP_ENTRY_PATH}")
            return

        self.console.print("[cyan]>[/cyan] Creating desktop entry...")
        DESKTOP_ENTRY_PATH.write_text(desktop_content)
        self.console.print(f"[green][OK][/green] Desktop entry created")

    def verify_installation(self) -> Optional[str]:
        """Verify Firefox was installed correctly and return version."""
        firefox_bin = INSTALL_DIR / "firefox"
        if not firefox_bin.exists():
            return None

        if self.dry_run:
            return "DRY RUN"

        try:
            result = subprocess.run(
                [str(firefox_bin), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def install(self, progress_callback=None) -> str:
        """Run the full installation process."""
        self.console.print("\n[bold blue]firefox-rebuild[/bold blue] — Installing Firefox\n")

        if not self.dry_run and not self.check_root():
            self.console.print("[red]This needs root privileges. Re-run with sudo.[/red]")
            raise PermissionError("Root required")

        self.remove_old_firefox()
        tarball = self.download_firefox(progress_callback)
        try:
            self.extract_firefox(tarball)
            self.create_symlink()
            self.create_desktop_entry()
            version = self.verify_installation()
            return version or "unknown"
        finally:
            # Clean up downloaded tarball
            if tarball.exists() and not self.dry_run:
                tarball.unlink(missing_ok=True)

        return "unknown"