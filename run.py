#!/usr/bin/env python3
"""
Quick runner for firefox-rebuild — works without pip or git.
Run with: sudo python3 run.py [install|status|version|uninstall]
"""

import os
import sys

# Ensure src/ is in python path
repo_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from firefox_rebuild.cli import app

if __name__ == "__main__":
    args = sys.argv[1:]
    known_commands = {"install", "version", "uninstall", "status", "-h", "--help"}
    if not args:
        args = ["install"]
    elif args[0] not in known_commands and args[0].startswith("-"):
        args = ["install"] + args

    sys.exit(app(args))
