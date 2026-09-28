#!/usr/bin/env bash
set -e

# firefox-rebuild quick installer script for lab environments
# Usage: sudo ./install.sh [options]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 is required but not found."
    echo "    Please install python3 using your package manager (e.g. apt install python3)"
    exit 1
fi

# Run the installer using pure standard library
python3 "$SCRIPT_DIR/run.py" "$@"
