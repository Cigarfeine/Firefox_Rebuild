"""
CLI interface — the friendly face of firefox-rebuild.
Standard library only, zero external dependencies required.
"""

import argparse
import ctypes
import os
import shutil
import subprocess
import sys
import time
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from .installer import Console, FirefoxInstaller, console

REFRESH_INTERVAL = 0.1

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
    console.print(BANNER.strip(), style="bold cyan")
    print()


def print_success(version: str) -> None:
    console.print(SUCCESS_BANNER.strip(), style="bold green")
    console.print(f"\n[bold]Firefox {version}[/bold] is ready to go [green](fox)[/green]\n")


def print_table(rows: list[tuple[str, str, str]], headers: Optional[list[str]] = None) -> None:
    """Print a clean formatted table using pure standard library."""
    if not rows and not headers:
        return

    all_data: list[tuple[str, ...]] = [tuple(headers)] if headers else []
    all_data.extend(rows)
    num_cols = max(len(r) for r in all_data)

    col_widths = [0] * num_cols
    for row in all_data:
        for idx, col in enumerate(row):
            clean_text = Console()._format(str(col))
            # Strip ANSI escape codes when calculating column width
            for tag in Console._TAGS.values():
                clean_text = clean_text.replace(tag, "")
            clean_text = clean_text.replace(Console._RESET, "")
            col_widths[idx] = max(col_widths[idx], len(clean_text))

    if headers:
        header_line = "  ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
        console.print(f"[bold cyan]{header_line}[/bold cyan]")
        console.print("[dim]" + "─" * (sum(col_widths) + (num_cols - 1) * 2) + "[/dim]")

    for row in rows:
        row_parts = []
        for i, val in enumerate(row):
            width = col_widths[i]
            row_parts.append(f"{str(val):<{width}}")
        console.print("  ".join(row_parts))
    print()


# ── Progress helpers ──────────────────────────────────────────────────


class DownloadProgress:
    """A smooth zero-dependency download progress bar with speed and ETA."""

    def __init__(self, description: str = "Downloading Firefox") -> None:
        self.description = description
        self.start_time: float = 0.0
        self.last_update_time: float = 0.0
        self.total: int = 0
        self.is_tty = sys.stdout.isatty()

    def start(self, total: int = 0) -> None:
        self.total = total
        self.start_time = time.time()
        self.last_update_time = self.start_time
        if self.is_tty:
            sys.stdout.write(f"\r[cyan]>[/cyan] {self.description}... ")
            sys.stdout.flush()

    def update(self, downloaded: int, total: int) -> None:
        if not self.is_tty:
            return

        now = time.time()
        # Limit update rate to avoid flickering
        if now - self.last_update_time < REFRESH_INTERVAL and downloaded < total:
            return
        self.last_update_time = now

        self.total = total or self.total
        percent = (downloaded / self.total * 100) if self.total > 0 else 0
        elapsed = max(now - self.start_time, 0.001)
        speed_bps = downloaded / elapsed
        speed_mbps = speed_bps / (1024 * 1024)

        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = self.total / (1024 * 1024)

        bar_len = 25
        filled_len = int(bar_len * (downloaded / self.total)) if self.total > 0 else 0
        bar = "█" * filled_len + "░" * (bar_len - filled_len)

        eta_str = "--:--"
        if speed_bps > 0 and self.total > downloaded:
            rem_sec = int((self.total - downloaded) / speed_bps)
            eta_str = f"{rem_sec // 60:02d}:{rem_sec % 60:02d}"

        line = (
            f"\r\033[K[cyan]>[/cyan] {self.description}: [{bar}] "
            f"{percent:5.1f}% • {downloaded_mb:.1f}/{total_mb:.1f} MB • "
            f"{speed_mbps:.1f} MB/s • ETA {eta_str}"
        )
        sys.stdout.write(line)
        sys.stdout.flush()

    def finish(self) -> None:
        if self.is_tty:
            sys.stdout.write("\n")
            sys.stdout.flush()


@contextmanager
def spinner(message: str) -> Iterator[None]:
    """Simple spinner placeholder."""
    console.print(f"[cyan]>[/cyan] {message}...")
    try:
        yield
    finally:
        pass


# ── Commands ──────────────────────────────────────────────────────────


def cmd_install(dry_run: bool = False, yes: bool = False, verbose: bool = False) -> int:
    """Install or update Firefox to the latest version."""
    print_banner()

    if dry_run:
        console.print("[yellow][TEST] DRY RUN MODE — no changes will be made[/yellow]\n")

    if not Path("/etc/debian_version").exists() and not Path("/etc/lsb-release").exists():
        console.print("[yellow][!][/yellow] This tool is designed for Debian/Ubuntu-based systems.")
        console.print("It might work on others, but no promises.\n")

    if not yes and not dry_run:
        try:
            prompt = "This will replace your current Firefox. Continue? [Y/n]: "
            choice = input(prompt).strip().lower()
            if choice in ("n", "no"):
                console.print("[yellow]Aborted.[/yellow]")
                return 0
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Aborted.[/yellow]")
            return 0

    installer = FirefoxInstaller(dry_run=dry_run)
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

        console.print("[bold]Installation Summary:[/bold]")
        print_table(
            [
                ("Install location", ":", "/opt/firefox"),
                ("Command", ":", "firefox (via /usr/bin/firefox)"),
                ("Desktop entry", ":", "/usr/share/applications/firefox.desktop"),
                ("Version", ":", version),
            ]
        )

        if not dry_run:
            console.print(
                "\n[dim]Tip:[/dim] Run [bold]firefox[/bold] from terminal or "
                "find it in your app menu."
            )
            console.print(
                "[dim]Note:[/dim] This Firefox updates itself automatically. "
                "Run this tool again when you want the latest build.\n"
            )
        return 0

    except PermissionError:
        console.print("\n[red]Need root privileges. Try:[/red]")
        console.print(
            "  [bold]sudo firefox-rebuild install[/bold] (or [bold]sudo ./install.sh[/bold])"
        )
        return 1
    except Exception as e:
        if not dry_run:
            download_progress.finish()
        console.print(f"\n[red]Installation failed:[/red] {e}")
        if verbose:
            console.print(traceback.format_exc())
        return 1


def cmd_version() -> int:
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
    return 0


def cmd_uninstall(yes: bool = False) -> int:
    """Remove the manually installed Firefox."""
    print_banner()

    if not yes:
        try:
            choice = input("Remove /opt/firefox and associated files? [y/N]: ").strip().lower()
            if choice not in ("y", "yes"):
                console.print("[yellow]Aborted.[/yellow]")
                return 0
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Aborted.[/yellow]")
            return 0

    is_admin = False
    if hasattr(os, "geteuid"):
        is_admin = os.geteuid() == 0
    else:
        try:
            windll = getattr(ctypes, "windll", None)
            if windll is not None:
                is_admin = bool(windll.shell32.IsUserAnAdmin() != 0)
        except Exception:
            pass

    if not is_admin:
        console.print("[red]Need root privileges. Try:[/red]")
        console.print("  [bold]sudo firefox-rebuild uninstall[/bold]")
        return 1

    install_dir = Path("/opt/firefox")
    if install_dir.exists():
        shutil.rmtree(install_dir)
        console.print(f"[green][OK][/green] Removed {install_dir}")

    symlink = Path("/usr/bin/firefox")
    if symlink.exists() and symlink.is_symlink():
        symlink.unlink()
        console.print(f"[green][OK][/green] Removed symlink {symlink}")

    desktop = Path("/usr/share/applications/firefox.desktop")
    if desktop.exists():
        desktop.unlink()
        console.print("[green][OK][/green] Removed desktop entry")

    console.print("\n[green]Done.[/green] Firefox has been removed.")
    console.print("[dim]Note:[/dim] System package (apt firefox) was not touched.")
    return 0


def cmd_status() -> int:
    """Check Firefox installation status."""
    print_banner()

    rows: list[tuple[str, str, str]] = []

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
            rows.append(("/opt/firefox", "[green][OK] Installed[/green]", result.stdout.strip()))
        except subprocess.CalledProcessError:
            rows.append(
                (
                    "/opt/firefox",
                    "[yellow][!] Present but broken[/yellow]",
                    "Binary exists but --version failed",
                )
            )
    else:
        rows.append(("/opt/firefox", "[red][X] Not found[/red]", ""))

    # Check symlink
    symlink = Path("/usr/bin/firefox")
    if symlink.exists():
        if symlink.is_symlink():
            target = symlink.readlink()
            rows.append(("Symlink", "[green][OK] Exists[/green]", f"-> {target}"))
        else:
            rows.append(("Symlink", "[yellow][!] Exists but not a symlink[/yellow]", str(symlink)))
    else:
        rows.append(("Symlink", "[red][X] Missing[/red]", ""))

    # Check desktop entry
    desktop = Path("/usr/share/applications/firefox.desktop")
    if desktop.exists():
        rows.append(("Desktop entry", "[green][OK] Exists[/green]", str(desktop)))
    else:
        rows.append(("Desktop entry", "[red][X] Missing[/red]", ""))

    # Check system package
    try:
        result = subprocess.run(
            ["dpkg", "-l", "firefox"],
            capture_output=True,
            text=True,
            check=False,
        )
        if "ii  firefox" in result.stdout:
            rows.append(
                (
                    "System package (apt)",
                    "[yellow][!] Installed[/yellow]",
                    "Consider removing with apt",
                )
            )
        else:
            rows.append(("System package (apt)", "[green][OK] Not installed[/green]", ""))
    except FileNotFoundError:
        rows.append(("System package (apt)", "[dim]? Unknown[/dim]", "dpkg not available"))

    console.print("[bold cyan]Firefox Status[/bold cyan]")
    print_table(rows, headers=["Component", "Status", "Details"])
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="firefox-rebuild",
        description="A friendly Firefox installer for lab environments — zero dependencies needed.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # install command
    install_parser = subparsers.add_parser("install", help="Install or update Firefox")
    install_parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Show what would happen without making changes"
    )
    install_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    install_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    # version command
    subparsers.add_parser("version", help="Show installed Firefox version")

    # uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove manually installed Firefox")
    uninstall_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )

    # status command
    subparsers.add_parser("status", help="Check Firefox installation status")

    return parser


def app(args: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    if args is None:
        args = sys.argv[1:]

    parser = build_parser()
    if not args:
        print_banner()
        parser.print_help()
        return 0

    parsed = parser.parse_args(args)

    if parsed.command == "install":
        return cmd_install(dry_run=parsed.dry_run, yes=parsed.yes, verbose=parsed.verbose)
    elif parsed.command == "version":
        return cmd_version()
    elif parsed.command == "uninstall":
        return cmd_uninstall(yes=parsed.yes)
    elif parsed.command == "status":
        return cmd_status()
    else:
        print_banner()
        parser.print_help()
        return 0


def main() -> None:
    """Entry point for console script."""
    sys.exit(app())


if __name__ == "__main__":
    main()
