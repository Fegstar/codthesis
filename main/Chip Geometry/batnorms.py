#!/usr/bin/env python3
"""
run_bat.py – launch a Windows batch file cleanly
- opens a new console window for the .bat
- returns immediately (script keeps running in the background)
- raises a helpful exception if the .bat isn’t found
"""

from pathlib import Path
import subprocess
import sys
import os

# ---------------------------------------------------------------------------
# EDIT ME: full path to your batch file
BAT_PATH = r"C:\Users\ougbine\BatchFile.bat"
# ---------------------------------------------------------------------------

def run_batch(bat_file: str) -> None:
    bat = Path(bat_file).resolve()
    if not bat.exists():
        sys.exit(f"[ERROR] Batch file not found: {bat}")

    # `cmd /c` → run the command then close
    # CREATE_NEW_CONSOLE → open in its own window (no interference with Python)
    creation_flags = subprocess.CREATE_NEW_CONSOLE

    try:
        subprocess.Popen(
            ["cmd", "/c", str(bat)],
            creationflags=creation_flags,
        )
        print("✓  Batch file launched in a new window.")
    except OSError as exc:          # covers *all* launch failures
        sys.exit(f"[ERROR] Could not start batch file: {exc.strerror}")

if __name__ == "__main__":
    run_batch(BAT_PATH)
