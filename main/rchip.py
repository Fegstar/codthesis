#!/usr/bin/env python3
"""
rchip.py — multiply the FIRST Johnson-Cook *Rate Dependent parameter by 1.5
           and launch an Abaqus job.

INPUT : S-3193_SDIN_modified.inp  (must be beside this script)
OUTPUT: rchipInp.inp              (modified copy)
        rchip.odb                 (created by Abaqus)
"""

import os
import sys
import shutil
import subprocess
import re

# -------- user-editable section ---------------------------------------------
ABAQUS_CMD   = "abaqus"            # change to abq2022.bat or full path if needed
INPUT_INP    = "C:\\Users\\ougbine\\Href_modified.inp"
OUTPUT_INP   = "rchipInp.inp"
JOB_NAME     = "rchipInp"
SCALE_FACTOR = 1.2                   # ← put your desired multiplier here
# -----------------------------------------------------------------------------


def modify_rate_first_value(inp: str, out: str, factor: float = 1.0) -> None:
    """
    Find '*Rate Dependent, type=JOHNSON COOK' and in the next line
    multiply the FIRST comma-separated value by `factor`.
    """
    if not os.path.isfile(inp):
        raise FileNotFoundError(f"Input INP '{inp}' not found.")

    with open(inp, "r") as fin:
        lines = fin.readlines()

    out_lines, i = [], 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)

        if line.strip().lower().startswith("*rate dependent") and "johnson cook" in line.lower():
            if i + 1 >= len(lines):
                raise RuntimeError("Found Johnson-Cook rate keyword with no value line.")

            raw = lines[i + 1].rstrip("\n")
            parts = [p.strip() for p in raw.split(",")]

            if len(parts) < 1 or parts[0] == "":
                raise ValueError("Could not parse FIRST Johnson-Cook rate parameter.")

            # keep original precision
            orig_text = parts[0]
            try:
                orig_val = float(orig_text)
            except ValueError:
                raise ValueError(f"Unable to convert '{orig_text}' to float.")

            dec_match = re.search(r"\.(\d+)", orig_text)
            fmt = f"{{:.{len(dec_match.group(1))}f}}" if dec_match else "{:.6f}"
            parts[0] = fmt.format(orig_val * factor)

            trailing = "," if raw.strip().endswith(",") else ""
            out_lines.append(", ".join(parts) + trailing + "\n")
            i += 2
            continue

        i += 1

    with open(out, "w") as fout:
        fout.writelines(out_lines)
    print(f"✓ Modified INP written to: {out}")


def run_abaqus_job(inp_file: str, job_name: str,
                   cpus: int = 1, memory: str = "2GB") -> None:
    """Launch Abaqus and raise on failure."""
    if not os.path.isfile(inp_file):
        raise FileNotFoundError(f"INP file '{inp_file}' not found.")

    if shutil.which(ABAQUS_CMD) is None:
        raise FileNotFoundError(
            f"Could not find '{ABAQUS_CMD}'. Add its directory to PATH or set ABAQUS_CMD."
        )

    cmd = (f'{ABAQUS_CMD} job={job_name} input="{inp_file}" '
           f'cpus={cpus} memory={memory} interactive')
    print("→ Launching Abaqus:\n  " + cmd)

    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(f"Abaqus job '{job_name}' failed (return code {result.returncode}).")


if __name__ == "__main__":
    here    = os.path.dirname(os.path.abspath(__file__))
    inp_in  = os.path.join(here, INPUT_INP)
    inp_out = os.path.join(here, OUTPUT_INP)

    print(f"Modifying FIRST Johnson-Cook rate value in '{inp_in}' ×{SCALE_FACTOR} …")
    modify_rate_first_value(inp_in, inp_out, factor=SCALE_FACTOR)

    print(f"Running Abaqus job '{JOB_NAME}' …")
    run_abaqus_job(inp_out, JOB_NAME)
    print(f"✓ Done. Check for '{JOB_NAME}.odb' in {here}.")
