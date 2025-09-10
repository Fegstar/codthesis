#!/usr/bin/env python
"""
Forceprompt.py
--------------
1. Runs CutForce.py in Abaqus/CAE no-GUI mode on the selected ODB.
2. Reads Function_Script.py and extracts:
     • new_inelastic_params
     • new_plastic_params
     • new_rate_params
3. Reads out/<study>.hrf created by CutForce.py
4. Packs everything into forceext.json
"""

import subprocess, sys, pathlib, json, re

# ------------------------------------------------------------------ #
#  User paths (edit if needed)
# ------------------------------------------------------------------ #
ABAQUS_CMD   = "abaqus"
CUTFORCE_PY  = r"C:\Users\Ougbine\CutForce.py"
FUNC_SCRIPT  = r"C:\Users\Ougbine\Function_Script.py"
DEFAULT_ODB  = r"C:\Users\Ougbine\Yil.odb"

FORCEEXT_PATH = pathlib.Path("forceext.json")   # <- final output
# ------------------------------------------------------------------ #

# ------- choose the ODB ------------------------------------------- #
odb_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(DEFAULT_ODB)
if not odb_path.is_file():
    sys.exit(f"ODB not found: {odb_path}")

study      = odb_path.stem
hrf_path   = pathlib.Path("out") / f"{study}.hrf"

# ------- run CutForce.py in Abaqus -------------------------------- #
cmd = f'{ABAQUS_CMD} cae noGUI="{CUTFORCE_PY}" -- -odb "{odb_path}"'
print("Running:", cmd, "\n")
try:
    subprocess.run(cmd, shell=True, check=True)
except subprocess.CalledProcessError as e:
    sys.exit(f"Abaqus exited with error code {e.returncode}")

# ------- grab the three strings from Function_Script.py ----------- #
fs_path = pathlib.Path(FUNC_SCRIPT)
if not fs_path.is_file():
    sys.exit(f"Function_Script.py not found at {fs_path}")

text = fs_path.read_text(encoding="utf-8")

def grab(name):
    m = re.search(rf'{name}\s*=\s*["\']([^"\']+)["\']', text)
    return m.group(1) if m else None

inelastic = grab("new_inelastic_params")
plastic   = grab("new_plastic_params")
rate      = grab("new_rate_params")

print("Parameters found:")
print("  inelastic :", inelastic)
print("  plastic   :", plastic)
print("  rate      :", rate)

# ------- read the forces from the HRF written by CutForce.py ------ #
if not hrf_path.is_file():
    sys.exit(f"Expected {hrf_path} but the file is missing.")

with hrf_path.open("r", encoding="utf-8") as fp:
    data = json.load(fp)

# ------- merge and write to forceext.json -------------------------- #
data.update({
    "inelastic_params": inelastic,
    "plastic_params"  : plastic,
    "rate_params"     : rate
})

with FORCEEXT_PATH.open("w", encoding="utf-8") as fp:
    json.dump(data, fp, indent=2)

print(f"\nSaved full set to {FORCEEXT_PATH.resolve()}")
print(json.dumps(data, indent=2))
print("\nDone.")
