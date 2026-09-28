"""
Entry point for running package directly: python3 -m firefox_rebuild
"""

import sys
from firefox_rebuild.cli import app

if __name__ == "__main__":
    sys.exit(app())
