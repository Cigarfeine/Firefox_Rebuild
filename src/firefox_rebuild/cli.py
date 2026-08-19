"""
CLI interface — the friendly face of firefox-rebuild.
"""

import ctypes
import os
import shutil
import subprocess
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.spinner import Spinner
from rich.table import Table

from .installer import FirefoxInstaller

app = typer.Typer(
    name="firefox-rebuild",
    help="A friendly Firefox installer for lab environments",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# ── Visual flair ──────────────────────────────────────────────────────

BANNER = r"""
+--------------------------------------------------------------+
|                                                              |
|    ___ _            _     _ _  ___ _   _ ____                |
|   / _ \ |__   __ _| |__ | | |/ _ \ | | | |  _ \              |
|  | | | | '_ \ / _` | '_ \| | | | | | | | | |_) |             |
|  | |_| | |_) | (_| | |_) | | | |_| | |_| |  _ <              |
|   \___/|_.__/ \__,_|_.__/|_|_|\___/ \__,_|_| \_\             |
|                                                              |
|           [dim]rebuild[/dim] — lab-friendly Firefox installer          |
+--------------------------------------------------------------+
"""

SUCCESS_BANNER = r"""
+--------------------------------------------------------------+
|                                                              |
|     ____  _   _ ____    ___ ____ ____  ____                  |
|    / ___|| | | |  _ \  |_ _/ ___|  _ \|  _ \                 |
|    \___ \| | | | |_) |  | | |   | |_) | | | |                |
|     ___) | |_| |  _ <   | | |___|  _ <| |_| |                |
|    |____/ \___/|_| \_\ |___\____|_| \_\____/                 |
|                                                              |
+--------------------------------------------------------------+
"""


def print_banner() -> None:
    console.print(BANNER, style="bold cyan")


def print_success(version: str) -> None:
    console.print(SUCCESS_BANNER, style="bold green")
    console.print(f"\n[bold]Firefox {version}[/bold] is ready to go [green](fox)[/green]\n")


# ── Progress helpers ──────────────────────────────────────────────────


class DownloadProgress:
    """A nice download progress bar with speed and ETA."""

    def __init__(self) -> None:
        self.progress = Progress(
            SpinnerColumn("dots", style="cyan"),
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=40, style="cyan", complete_style="green"),
            TaskProgressColumn(),
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=console,
            transient=True,
        )
        self.task_id: Optional[TaskID] = None
        self._live: Optional[Live] = None

    def start(self, description: str = "Downloading Firefox") -> None:
        self.task_id = self.progress.add_task(description, total=100)
        self._live = Live(self.progress, console=console, refresh_per_second=10)
        self._live.start()

    def update(self, downloaded: int, total: int) -> None:
        if self.task_id is not None and total > 0:
            self.progress.update(self.task_id, completed=downloaded, total=total)

    def finish(self) -> None:
        if self._live:
            self._live.stop()
            self._live = None


@contextmanager
def spinner(message: str) -> Iterator[None]:
    """A simple spinner context manager."""
    spin = Spinner("dots", text=f"[cyan]{message}[/cyan]")
    live = Live(spin, console=console, refresh_per_second=10)
    live.start()
    try:
        yield
    finally:
        live.stop()


# ── Commands ──────────────────────────────────────────────────────────


@app.command()
def install(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would happen without making changes"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """
    Install or update Firefox to the latest version.

    This removes any existing Firefox (system package or manual install),
    grabs the latest build directly from Mozilla, and sets it up properly
    with a symlink and desktop entry.
    """
    print_banner()

    if dry_run:
        console.print("[yellow][TEST] DRY RUN MODE — no changes will be made[/yellow]\n")

    # Check if we're on a supported system
    if not Path("/etc/debian_version").exists() and not Path("/etc/lsb-release").exists():
        console.print("[yellow][!][/yellow] This tool is designed for Debian/Ubuntu-based systems.")
        console.print("It might work on others, but no promises.\n")

    if not yes and not dry_run:
        confirm = typer.confirm(
            "This will replace your current Firefox. Continue?",
            default=True,
        )
        if not confirm:
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit(0)

    installer = FirefoxInstaller(dry_run=dry_run)

    # Progress tracking
    download_progress = DownloadProgress()

    def progress_callback(downloaded: int, total: int) -> None:
        download_progress.update(downloaded, total)

    try:
        if not dry_run:
            download_progress.start()

        version = installer.install(progress_callback=progress_callback)

        if not dry_run:
            download_progress.finish()

        print_success(version)

        # Show what was installed
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Property", style="dim")
        table.add_column("Value", style="bold")
        table.add_row("Install location", "/opt/firefox")
        table.add_row("Command", "firefox (via /usr/bin/firefox)")
        table.add_row("Desktop entry", "/usr/share/applications/firefox.desktop")
        table.add_row("Version", version)
        console.print(table)

        if not dry_run:
            console.print(
                "\n[dim]Tip:[/dim] Run [bold]firefox[/bold] from terminal or "
                "find it in your app menu."
            )
            console.print(
                "[dim]Note:[/dim] This Firefox updates itself automatically. "
                "Run this tool again when you want the very latest build.\n"
            )

    except PermissionError:
        console.print("\n[red]Need root privileges. Try:[/red]")
        console.print("  [bold]sudo firefox-rebuild install[/bold]")
        raise typer.Exit(1) from None
    except Exception as e:
        if not dry_run:
            download_progress.finish()
        console.print(f"\n[red]Installation failed:[/red] {e}")
        if verbose:
            console.print(traceback.format_exc())
        raise typer.Exit(1) from None


@app.command()
def version() -> None:
    """Show the installed Firefox version."""
    print_banner()

    firefox_bin = Path("/opt/firefox/firefox")
    if firefox_bin.exists():
        try:
            result = subprocess.run(
                [str(firefox_bin), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            version = result.stdout.strip()
            console.print(f"[green]Installed:[/green] {version}")
        except subprocess.CalledProcessError:
            console.print("[yellow]Firefox is installed but --version failed[/yellow]")
    else:
        console.print("[yellow]Firefox not found in /opt/firefox[/yellow]")

    # Also check system firefox
    try:
        result = subprocess.run(
            ["firefox", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            console.print(f"[dim]System firefox:[/dim] {result.stdout.strip()}")
    except FileNotFoundError:
        pass


@app.command()
def uninstall(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Remove the manually installed Firefox."""
    print_banner()

    if not yes:
        confirm = typer.confirm("Remove /opt/firefox and associated files?", default=False)
        if not confirm:
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit(0)

    # Check root/admin
    is_admin = False
    if hasattr(os, "geteuid"):
        is_admin = os.geteuid() == 0
    else:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            pass

    if not is_admin:
        console.print("[red]Need root privileges. Try:[/red]")
        console.print("  [bold]sudo firefox-rebuild uninstall[/bold]")
        raise typer.Exit(1)

    # Remove installation
    install_dir = Path("/opt/firefox")
    if install_dir.exists():
        shutil.rmtree(install_dir)
        console.print(f"[green][OK][/green] Removed {install_dir}")

    # Remove symlink
    symlink = Path("/usr/bin/firefox")
    if symlink.exists() and symlink.is_symlink():
        symlink.unlink()
        console.print(f"[green][OK][/green] Removed symlink {symlink}")

    # Remove desktop entry
    desktop = Path("/usr/share/applications/firefox.desktop")
    if desktop.exists():
        desktop.unlink()
        console.print("[green][OK][/green] Removed desktop entry")

    console.print("\n[green]Done.[/green] Firefox has been removed.")
    console.print("[dim]Note:[/dim] System package (apt firefox) was not touched.")


@app.command()
def status() -> None:
    """Check Firefox installation status."""
    print_banner()

    table = Table(title="Firefox Status", show_header=True, header_style="bold cyan")
    table.add_column("Component", style="bold")
    table.add_column("Status")
    table.add_column("Details", style="dim")

    # Check /opt/firefox
    install_dir = Path("/opt/firefox")
    if install_dir.exists():
        try:
            result = subprocess.run(
                [str(install_dir / "firefox"), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            table.add_row("/opt/firefox", "[green][OK] Installed[/green]", result.stdout.strip())
        except subprocess.CalledProcessError:
            table.add_row(
                "/opt/firefox",
                "[yellow][!] Present but broken[/yellow]",
                "Binary exists but --version failed",
            )
    else:
        table.add_row("/opt/firefox", "[red][X] Not found[/red]", "")

    # Check symlink
    symlink = Path("/usr/bin/firefox")
    if symlink.exists():
        if symlink.is_symlink():
            target = symlink.readlink()
            table.add_row("Symlink", "[green][OK] Exists[/green]", f"-> {target}")
        else:
            table.add_row("Symlink", "[yellow][!] Exists but not a symlink[/yellow]", str(symlink))
    else:
        table.add_row("Symlink", "[red][X] Missing[/red]", "")

    # Check desktop entry
    desktop = Path("/usr/share/applications/firefox.desktop")
    if desktop.exists():
        table.add_row("Desktop entry", "[green][OK] Exists[/green]", str(desktop))
    else:
        table.add_row("Desktop entry", "[red][X] Missing[/red]", "")

    # Check system package
    try:
        result = subprocess.run(
            ["dpkg", "-l", "firefox"],
            capture_output=True,
            text=True,
            check=False,
        )
        if "ii  firefox" in result.stdout:
            table.add_row(
                "System package (apt)",
                "[yellow][!] Installed[/yellow]",
                "Consider removing with apt",
            )
        else:
            table.add_row("System package (apt)", "[green][OK] Not installed[/green]", "")
    except FileNotFoundError:
        table.add_row("System package (apt)", "[dim]? Unknown[/dim]", "dpkg not available")

    console.print(table)


if __name__ == "__main__":
    app()
