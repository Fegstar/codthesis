#!/usr/bin/env python
"""
run_cutforce.py  ·  **Abaqus → forces→JSON**
---------------------------------------------------------------
1. Launches *mEXTForce.py* inside Abaqus/CAE (no‑GUI) on the chosen ODB.
2. Expects that script to write `out/<study>.hrf` (JSON) containing
   **force_c** and **force_p**.
3. Reads those two numbers, shows them on the terminal, and packs them—
   together with the full stdout/stderr log—into **mForce.json**.

If the HRF file is missing or the keys aren’t present, a warning is
printed and the JSON file is still written (minus the missing fields).
"""

import subprocess, sys, json, pathlib, datetime

# ------------------------------------------------------------------ #
# USER SETTINGS                                                      #
# ------------------------------------------------------------------ #
ABAQUS_CMD   = "abaqus"   # or full path to abaqus.bat if not in %PATH%
CUTFORCE_PY  = r"C:\Users\Ougbine\m\mEXTForce.py"
DEFAULT_ODB  = r"C:\Users\Ougbine\mChipInp.odb"
# ------------------------------------------------------------------ #

# --- decide which ODB to analyse ---------------------------------- #
odb_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(DEFAULT_ODB)
if not odb_path.is_file():
    sys.exit(f"ODB not found: {odb_path}")

study    = odb_path.stem               # e.g.  mChip  →  mChip.hrf
hrf_path = pathlib.Path("out") / f"{study}.hrf"

# --- build & run the Abaqus command -------------------------------- #
cmd = f'{ABAQUS_CMD} cae noGUI="{CUTFORCE_PY}" -- -odb "{odb_path}"'
print("Running:", cmd, "\n")

result = subprocess.run(
    cmd,
    shell=True,
    text=True,
    capture_output=True  # keep stdout / stderr
)

stdout, stderr = result.stdout, result.stderr

# --- extract Force_C / Force_P from the HRF ------------------------ #
force_c = force_p = None
if hrf_path.is_file():
    try:
        with hrf_path.open("r", encoding="utf-8") as fp:
            hrf = json.load(fp)
        force_c = hrf.get("force_c")
        force_p = hrf.get("force_p")
        print("  → force_c :", force_c)
        print("  → force_p :", force_p)
    except Exception as exc:
        print(f"  ! Could not parse {hrf_path}: {exc}")
else:
    print(f"  ! Expected {hrf_path} but it does not exist.")

# --- assemble and dump mForce.json -------------------------------- #
record = {
    "timestamp" : datetime.datetime.now().isoformat(timespec="seconds"),
    "command"   : cmd,
    "odb"       : str(odb_path.resolve()),
    "returncode": result.returncode,
    "stdout"    : stdout,
    "stderr"    : stderr,
}
if force_c is not None:
    record["force_c"] = force_c
if force_p is not None:
    record["force_p"] = force_p

json_path = pathlib.Path("mForce.json").resolve()
with json_path.open("w", encoding="utf-8") as fp:
    json.dump(record, fp, indent=2)

print(f"\n✔  Results written to {json_path}")
