# -*- coding: utf-8 -*-
r"""
Quick extractor for **cutting** (Fc) and **penetration / passive** (Fp)
forces from an Abaqus ODB.

• No auxiliary JSON, no extra arguments – the only input is the ODB file.
• By default it opens  `C:\\Users\\Ougbine\\Code.odb`,
  but you can override that with the command‑line flag
  `-odb <other_file.odb>` if you wish.
• Forces are reported as **N** (not divided by element depth).
  If you run a 2‑D CEL model and want N/mm, simply set the constant
  `DIVISOR = <element_thickness>` below.
• Output:  a small JSON file   `out/<study>.hrf`   with
  `{ "force_c": Fc, "force_p": Fp }` and a console + log message.

Run example:
    abaqus cae noGUI=CutForce.py            # uses default path
    abaqus cae noGUI=CutForce.py -- -odb D:/jobs/Test.odb
"""

# --------------------------------------------------------------------------- #
#  Standard modules
# --------------------------------------------------------------------------- #
import os, sys, json, platform
from datetime import datetime

# Abaqus / odb modules ------------------------------------------------------ #
from odbAccess import openOdb, OdbError
from abaqusConstants import *

# --------------------------------------------------------------------------- #
#  User‑editable constants
# --------------------------------------------------------------------------- #
DEFAULT_ODB_PATH = "C:\\Users\\Ougbine\\TQChipInp.odb"  # change if you like
DIVISOR = 0.005                                            # 1.0 = keep forces in N

# --------------------------------------------------------------------------- #
#  Tiny logger – prints and writes to POSTSOLV.log
# --------------------------------------------------------------------------- #
_log_file = None

def log(msg):
    global _log_file
    if _log_file is None:
        _log_file = open("POSTSOLV.log", "w")
    stamp = datetime.now().strftime("%H:%M:%S")
    line  = f"[{stamp}] {msg}"
    print(line)
    _log_file.write(line + "\n")
    _log_file.flush()

# --------------------------------------------------------------------------- #
#  Get the ODB path (override via -odb)
# --------------------------------------------------------------------------- #
if "-odb" in sys.argv:
    try:
        odb_path = sys.argv[sys.argv.index("-odb") + 1]
    except IndexError:
        print("ERROR: -odb flag given without a file name")
        sys.exit(1)
else:
    odb_path = DEFAULT_ODB_PATH

study = os.path.splitext(os.path.basename(odb_path))[0]

log("Python inside Abaqus : " + platform.python_version())
log("Opening ODB          : " + odb_path)

try:
    odb = openOdb(odb_path)
except OdbError as e:
    log("!! Cannot open ODB – " + str(e))
    sys.exit(2)

# --------------------------------------------------------------------------- #
#  Locate reference‑point node set  TOOL-1 / SET-RP
# --------------------------------------------------------------------------- #
try:
    inst = odb.rootAssembly.instances["TOOL-1"]
    rp_nodes = inst.nodeSets["SET-RP"].nodes
except KeyError:
    log("!! Could not find instance 'TOOL-1' or node‑set 'SET-RP'")
    sys.exit(3)

node_labels = {n.label for n in rp_nodes}
log(f"Found {len(node_labels)} RP node(s) : {sorted(node_labels)}")

# --------------------------------------------------------------------------- #
#  Pick the step – prefer 'Step-1', else first available
# --------------------------------------------------------------------------- #
if "Step-1" in odb.steps:
    step_name = "Step-1"
else:
    step_name = list(odb.steps.keys())[0]
    log("Using first step in model : " + step_name)

step = odb.steps[step_name]

# --------------------------------------------------------------------------- #
#  Accumulate reaction forces over all frames
# --------------------------------------------------------------------------- #
rf_x = rf_y = 0.0
count = 0

for fr in step.frames:
    rf_field = fr.fieldOutputs["RF"]
    for val in rf_field.values:
        if val.nodeLabel in node_labels:
            rf_x += val.data[0]
            rf_y += val.data[1]
            count += 1

if count == 0:
    log("!! No RF data found for the RP node(s)")
    sys.exit(4)

Fc = abs(rf_x / count) / DIVISOR  # cutting  force (N or N/mm)
Fp = abs(rf_y / count) / DIVISOR  # passive force (N or N/mm)

log(f"Average cutting  force Fc = {Fc:.3f} N")
log(f"Average passive force Fp = {Fp:.3f} N")

# --------------------------------------------------------------------------- #
#  Write result to out/<study>.hrf
# --------------------------------------------------------------------------- #
out_dir = "out"
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

out_path = os.path.join(out_dir, study + ".hrf")
with open(out_path, "w") as f_out:
    json.dump({"force_c": Fc, "force_p": Fp}, f_out, indent=2)

log("Saved forces to " + out_path)
log("Done.")
