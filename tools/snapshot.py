#!/usr/bin/env python3
"""Freeze the current bot as a numbered baseline so new versions can be tested against it.

Usage:
    python tools/snapshot.py 5                  # copies bots/goldrush-cpp -> bots/goldrush-cpp-v5
    python tools/snapshot.py 5 goldrush         # copies bots/goldrush -> bots/goldrush-v5
    make eval OPPONENT=goldrush-cpp-v5          # does the new version beat the old one?

A change ships only if it beats the previous snapshot, not just the starter.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) not in (2, 3) or not sys.argv[1].isdigit():
        print(__doc__)
        return 1
    bot = sys.argv[2] if len(sys.argv) == 3 else "goldrush-cpp"
    source = ROOT / "bots" / bot
    target = ROOT / "bots" / f"{bot}-v{sys.argv[1]}"
    if target.exists():
        print(f"{target.name} already exists; pick a new number")
        return 1
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".cambc", "__pycache__", "build", "compile_commands.json"))
    print(f"snapshot written to bots/{target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
