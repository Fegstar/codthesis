#!/usr/bin/env python3
"""
run_bat.py — launch a Windows batch file in its own Command-Prompt window
"""

import subprocess
import pathlib
import sys

# --- EDIT ME:  full path to your .bat ---------------------------------------
BAT_PATH = r"C:\Users\ougbine\B\BBatchFile.bat"
# ----------------------------------------------------------------------------

def run_batch(bat_file: str) -> None:
    """Start the batch file in a separate cmd.exe window."""
    bat = pathlib.Path(bat_file)
    if not bat.is_file():
        sys.exit(f"Batch file not found: {bat}")

    # 'start' opens a new shell window; /c tells cmd to run the command then exit
    cmd = f'start "" cmd /c "{bat}"'
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("✓ Batch file launched successfully.")
    except subprocess.CalledProcessError as exc:
        print(f"✗ Error while launching batch file (return code {exc.returncode}).")
        raise  # re-raise if you want the Python script itself to fail

if __name__ == "__main__":
    run_batch(BAT_PATH)
