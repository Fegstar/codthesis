#!/usr/bin/env python3
"""
AChip.py  —  multiply the first Johnson-Cook plastic parameter by 1.5
             and launch an Abaqus job.

IN:
    S-3193_SDIN_modified.inp   (must reside beside this script)
OUT:
    AChipInp.inp               (modified copy)
    AChip.odb                  (created by Abaqus)

Only the *Plastic, hardening=JOHNSON COOK block is touched.
"""

import os
import sys
import shutil
import subprocess
import re

# -------- user-editable section ---------------------------------------------
ABAQUS_CMD   = "abaqus"            # change to abq2022.bat or full path if needed
INPUT_INP    = "C:\\Users\\ougbine\\Href_modified.inp"
OUTPUT_INP   = "AChipInp.inp"
JOB_NAME     = "AChipInp"
SCALE_FACTOR = 1.2                 # ← put your desired multiplier here
# -----------------------------------------------------------------------------


def modify_first_plastic_value(inp: str, out: str, factor: float = 1.0) -> None:
    """
    Locate '*Plastic, hardening=JOHNSON COOK' and multiply the FIRST value
    (A) on the next line by `factor`.  All other lines are copied verbatim.
    """
    if not os.path.isfile(inp):
        raise FileNotFoundError(f"Input INP '{inp}' not found.")

    with open(inp, "r") as fin:
        lines = fin.readlines()

    out_lines, i = [], 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)

        if line.strip().lower().startswith("*plastic") and "johnson cook" in line.lower():
            if i + 1 >= len(lines):
                raise RuntimeError(
                    "Found '*Plastic, hardening=JOHNSON COOK' with no value line."
                )

            raw_line = lines[i + 1].rstrip("\n")

            # Split on commas but keep empty trailing element if the line ends with ','
            parts = [p.strip() for p in raw_line.split(",")]

            if len(parts) < 1 or parts[0] == "":
                raise ValueError("Could not parse first Johnson-Cook parameter.")

            # Preserve original decimal precision
            first_val_text = parts[0]
            try:
                first_val_num = float(first_val_text)
            except ValueError:
                raise ValueError(f"Unable to convert '{first_val_text}' to float.")

            # Derive format from original (number of decimals)
            m = re.search(r"\.(\d+)", first_val_text)
            fmt = f"{{:.{len(m.group(1))}f}}" if m else "{:.6f}"
            parts[0] = fmt.format(first_val_num * factor)

            # Re-assemble line, preserving any trailing comma that was present
            trailing_comma = "," if raw_line.strip().endswith(",") else ""
            new_line = ", ".join(parts) + trailing_comma + "\n"

            out_lines.append(new_line)
            i += 2
            continue

        i += 1

    with open(out, "w") as fout:
        fout.writelines(out_lines)
    print(f"✓ Modified INP written to: {out}")


def run_abaqus_job(inp_file: str, job_name: str, cpus: int = 1, memory: str = "2GB") -> None:
    """Launch Abaqus; raise if executable not found or job fails."""
    if not os.path.isfile(inp_file):
        raise FileNotFoundError(f"INP file '{inp_file}' not found.")

    if shutil.which(ABAQUS_CMD) is None:
        raise FileNotFoundError(
            f"Could not find '{ABAQUS_CMD}'. Add its directory to PATH or set ABAQUS_CMD."
        )

    cmd = (
        f'{ABAQUS_CMD} job={job_name} input="{inp_file}" '
        f'cpus={cpus} memory={memory} interactive'
    )
    print("→ Launching Abaqus:\n  " + cmd)

    result = subprocess.run(cmd, shell=True)  # shell=True for *.bat convenience on Windows
    if result.returncode != 0:
        sys.exit(f"Abaqus job '{job_name}' failed (return code {result.returncode}).")


if __name__ == "__main__":
    here   = os.path.dirname(os.path.abspath(__file__))
    inp_in = os.path.join(here, INPUT_INP)
    inp_out = os.path.join(here, OUTPUT_INP)

    print(f"Modifying first Johnson-Cook parameter in '{inp_in}' ×{SCALE_FACTOR} …")
    modify_first_plastic_value(inp_in, inp_out, factor=SCALE_FACTOR)

    print(f"Running Abaqus job '{JOB_NAME}' …")
    run_abaqus_job(inp_out, JOB_NAME)
    print(f"✓ Done. Check for '{JOB_NAME}.odb' in {here}.")
