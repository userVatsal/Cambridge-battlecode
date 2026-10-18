#!/usr/bin/env python3
"""Freeze the current bot as a numbered baseline so new versions can be tested against it.

Usage:
    python tools/snapshot.py 2          # copies bots/goldrush -> bots/goldrush-v2
    make eval OPPONENT=goldrush-v2      # does the new version beat the old one?

A change ships only if it beats the previous snapshot, not just the starter.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print(__doc__)
        return 1
    source = ROOT / "bots" / "goldrush"
    target = ROOT / "bots" / f"goldrush-v{sys.argv[1]}"
    if target.exists():
        print(f"{target.name} already exists; pick a new number")
        return 1
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".cambc", "__pycache__"))
    print(f"snapshot written to bots/{target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
