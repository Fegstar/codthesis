#!/usr/bin/env python3
"""
TQChip.py  —  modify *Inelastic Heat Fraction by 1.5 and run Abaqus
"""

import os
import sys
import shutil
import subprocess

# -------- user-editable section ---------------------------------------------
ABAQUS_CMD = "abaqus"          # change to "abq2022.bat" or full path if needed
INPUT_INP  = "C:\\Users\\ougbine\\Href_modified.inp"
OUTPUT_INP = "TQChipInp.inp"
JOB_NAME   = "TQChipInp"
INEL_FACTOR = 1.05        # ← put your desired multiplier here
# ---------------------------------------------------------------------------


def process_inelastic_only(input_filename, output_filename, factor=1.0):
    if not os.path.isfile(input_filename):
        raise FileNotFoundError(f"Input INP '{input_filename}' not found.")

    with open(input_filename, "r") as fin:
        lines = fin.readlines()

    out_lines, i = [], 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)

        if line.strip().lower() == "*inelastic heat fraction":
            if i + 1 >= len(lines):
                raise RuntimeError("Keyword found but no value line follows.")
            raw = lines[i + 1].strip().rstrip(",")   # remove trailing comma
            try:
                val = float(raw)
            except ValueError:
                raise ValueError(f"Cannot convert '{raw}' to float.")
            out_lines.append(f"{val * factor:.7f}\n")
            i += 2
            continue
        i += 1

    with open(output_filename, "w") as fout:
        fout.writelines(out_lines)
    print(f"✓ Modified INP written to: {output_filename}")


def run_abaqus_job(inp_file, job_name, cpus=1, memory="2GB"):
    if not os.path.isfile(inp_file):
        raise FileNotFoundError(f"INP file '{inp_file}' not found.")

    # Verify Abaqus command exists
    if shutil.which(ABAQUS_CMD) is None:
        raise FileNotFoundError(
            f"Could not find '{ABAQUS_CMD}'. "
            "Add its directory to PATH or set ABAQUS_CMD to the full path."
        )

    cmd = (
        f'{ABAQUS_CMD} job={job_name} input="{inp_file}" '
        f'cpus={cpus} memory={memory} interactive'
    )
    print("→ Launching Abaqus:\n  " + cmd)

    # shell=True is convenient on Windows when calling *.bat
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(f"Abaqus job '{job_name}' failed (return code {result.returncode}).")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    inp_in  = os.path.join(here, INPUT_INP)
    inp_out = os.path.join(here, OUTPUT_INP)

    print(f"Processing '{inp_in}' (factor ×{INEL_FACTOR}) …")
    process_inelastic_only(inp_in, inp_out, factor=INEL_FACTOR)

    print(f"Running job '{JOB_NAME}' to create ODB …")
    run_abaqus_job(inp_out, JOB_NAME)
    print(f"✓ Done. Check for '{JOB_NAME}.odb' in {here}.")
