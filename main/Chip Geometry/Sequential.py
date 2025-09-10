#!/usr/bin/env python3
import subprocess
import time
import os

def run_script(path, display_name):
    """
    Attempt to run the given Python script, reporting success or error.
    Does not raise — errors are caught and logged so subsequent scripts still run.
    """
    if not os.path.exists(path):
        print(f"[ERROR] {display_name} not found at:\n    {path}\n")
        return

    print(f"🔄 Starting {display_name}...")
    try:
        subprocess.run(["python", path], check=True)
        print(f"✅ Finished {display_name}.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ {display_name} exited with error code {e.returncode}\n")
    except Exception as e:
        print(f"❌ Unexpected error running {display_name}: {e}\n")

def main():
    # Absolute paths to your scripts
    function_script   = "C:\\Users\\ougbine\\Function_Script.py"
    batnorms_script   = "C:\\Users\\ougbine\\Desktop\\Chip\\batnorms.py"
    processing_script = "C:\\Users\\ougbine\\Desktop\\Chip\\Processing.py"

    # 1) Run Function_Script.py
    run_script(function_script, "Function_Script.py")

    # 2) Run batnorms.py
    run_script(batnorms_script, "batnorms.py")

    # 3) Wait 10 seconds before running Processing.py
    print("⏳ Waiting 10 seconds before running Processing.py...")
    for remaining in range(10, 0, -1):
        print(f"  {remaining} seconds remaining...", end="\r")
        time.sleep(1)
    print("\n")

    # 4) Run Processing.py
    run_script(processing_script, "Processing.py")

    print("🎉 All done!")

if __name__ == "__main__":
    main()
