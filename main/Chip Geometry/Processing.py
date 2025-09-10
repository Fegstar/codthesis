#!/usr/bin/env python3
r"""
unified_move_params.py

Reads C:\Users\ougbine\abaqus.rpy, extracts:
  • Taylor_Quinney (from "Changing inelastic parameters → New")
  • JC_Hardening_ABNM first four values (from "Changing plastic parameters → New")
  • Strain_Rate_Hardening_Coefficient first value (from "Changing rate dependency parameters → New")
  • chip_thickness (from line containing "Distance Minimale")
  • Contact_Length (from line containing "Distance entre le premier ... sélectionné")

Then patches BOTH projects and prints all parameters clearly.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

ABAQUS_RPY = Path(r"C:\Users\ougbine\abaqus.rpy")

# Chip
CHIP_GRADIENT_PY = Path(r"C:\Users\ougbine\Desktop\Chip\Gradient.py")
CHIP_ERROR_PY    = Path(r"C:\Users\ougbine\Desktop\Chip\Error_Calculation.py")
CHIP_JSON_LOG    = Path(r"C:\Users\ougbine\Desktop\Chip\extracted_values.json")

# Contact Length
CL_GRADIENT_PY = Path(r"C:\Users\ougbine\Desktop\Contact_Length\Gradient.py")
CL_ERROR_PY    = Path(r"C:\Users\ougbine\Desktop\Contact_Length\Error_Calculation.py")
CL_JSON_LOG    = Path(r"C:\Users\ougbine\Desktop\Contact_Length\extracted_values.json")

FLOAT_RE = r"[-+]?(?:\d*\.\d+|\d+)"
P_INELASTIC_HDR = re.compile(r"^#:\s*Changing inelastic parameters:", re.I)
P_PLASTIC_HDR   = re.compile(r"^#:\s*Changing plastic parameters:",   re.I)
P_RATE_HDR      = re.compile(r"^#:\s*Changing rate dependency parameters:", re.I)

P_CHIP_LINE     = re.compile(r"Distance\s+Minimale", re.I)
P_CONTACT_LINE  = re.compile(r"Distance\s+entre\s+le\s+premier.*s[é|e]lectionn[é|e]\s*:", re.I)

def _numbers(s: str) -> List[float]:
    return [float(x) for x in re.findall(FLOAT_RE, s)]

def _value_line(lines: List[str], idx: int) -> str | None:
    for ln in lines[idx + 1:]:
        if "New:" in ln:
            return ln
    return None

def read_replay(path: Path) -> Tuple[float, List[float], List[float], float, float]:
    try:
        lines = path.read_text(encoding="latin-1", errors="ignore").splitlines()
    except FileNotFoundError:
        sys.exit(f"❌  Replay file not found: {path}")

    tq, abnm, c_val, chip_val, contact_val = None, None, None, None, None

    for i, ln in enumerate(lines):
        if tq is None and P_INELASTIC_HDR.search(ln):
            nxt = _value_line(lines, i)
            if nxt:
                nums = _numbers(nxt)
                if nums:
                    tq = nums[0]

        elif abnm is None and P_PLASTIC_HDR.search(ln):
            nxt = _value_line(lines, i)
            if nxt:
                nums = _numbers(nxt)
                if nums:
                    abnm = nums[:4]

        elif c_val is None and P_RATE_HDR.search(ln):
            nxt = _value_line(lines, i)
            if nxt:
                nums = _numbers(nxt)
                if nums:
                    c_val = nums[:1]

        if chip_val is None and P_CHIP_LINE.search(ln):
            nums = _numbers(ln)
            if nums:
                chip_val = nums[-1]

        if contact_val is None and P_CONTACT_LINE.search(ln):
            nums = _numbers(ln)
            if nums:
                contact_val = nums[-1]

        if None not in (tq, abnm, c_val, chip_val, contact_val):
            break

    if None in (tq, abnm, c_val, chip_val, contact_val):
        sys.exit("❌  Missing one or more required parameters from replay file.")

    return tq, abnm, c_val, chip_val, contact_val

def _patch_first(path: Path, pattern: str, repl: str, label: str) -> None:
    txt = path.read_text(encoding="cp1252", errors="replace")
    new_txt, n = re.subn(pattern, repl, txt, count=1, flags=re.MULTILINE)
    if n == 0:
        print(f"⚠️  {label} not found in {path} — nothing replaced.")
    else:
        path.write_text(new_txt, encoding="cp1252")
        print(f"✅  {label} updated in {path}")

def patch_chip(tq: float, abnm: List[float], c_val: List[float], chip_val: float) -> None:
    _patch_first(CHIP_GRADIENT_PY, r"^\s*Taylor_Quinney\s*=.*", f"    Taylor_Quinney = {tq}", "Chip: Taylor_Quinney")
    _patch_first(CHIP_GRADIENT_PY, r"^\s*JC_Hardening_ABNM\s*=.*", f"    JC_Hardening_ABNM = {abnm}", "Chip: JC_Hardening_ABNM")
    _patch_first(CHIP_GRADIENT_PY, r"^\s*Strain_Rate_Hardening_Coefficient\s*=.*", f"    Strain_Rate_Hardening_Coefficient = {c_val}", "Chip: Strain_Rate_Hardening_Coefficient")
    _patch_first(CHIP_GRADIENT_PY, r"^\s*chip_thickness\s*=.*", f"    chip_thickness = {chip_val}", "Chip: chip_thickness")
    _patch_first(CHIP_ERROR_PY, r"(Sim_Chip\s*=\s*)(\d+(?:\.\d+)?)+", rf"\g<1>{chip_val}", "Chip: Sim_Chip")
    CHIP_JSON_LOG.write_text(json.dumps({"Taylor_Quinney": tq, "JC_Hardening_ABNM": abnm, "Strain_Rate_Hardening_Coefficient": c_val, "chip_thickness": chip_val}, indent=4), encoding="utf-8")
    print(f"📄  Wrote {CHIP_JSON_LOG}")

def patch_contact(tq: float, abnm: List[float], c_val: List[float], contact_val: float) -> None:
    _patch_first(CL_GRADIENT_PY, r"^\s*Taylor_Quinney\s*=.*", f"    Taylor_Quinney = {tq}", "Contact: Taylor_Quinney")
    _patch_first(CL_GRADIENT_PY, r"^\s*JC_Hardening_ABNM\s*=.*", f"    JC_Hardening_ABNM = {abnm}", "Contact: JC_Hardening_ABNM")
    _patch_first(CL_GRADIENT_PY, r"^\s*Strain_Rate_Hardening_Coefficient\s*=.*", f"    Strain_Rate_Hardening_Coefficient = {c_val}", "Contact: Strain_Rate_Hardening_Coefficient")
    _patch_first(CL_GRADIENT_PY, r"^\s*Contact_Length\s*=.*", f"    Contact_Length = {contact_val}", "Contact: Contact_Length")
    _patch_first(CL_ERROR_PY, r"(Sim_Contact_Length\s*=\s*)(\d+(?:\.\d+)?)+", rf"\g<1>{contact_val}", "Contact: Sim_Contact_Length")
    CL_JSON_LOG.write_text(json.dumps({"Taylor_Quinney": tq, "JC_Hardening_ABNM": abnm, "Strain_Rate_Hardening_Coefficient": c_val, "Contact_Length": contact_val}, indent=4), encoding="utf-8")
    print(f"📄  Wrote {CL_JSON_LOG}")

def main() -> None:
    print("🔍  Reading:", ABAQUS_RPY)
    tq, abnm, c_val, chip_val, contact_val = read_replay(ABAQUS_RPY)

    print("\nParsed from replay (all parameters):")
    print("  Taylor_Quinney =", tq)
    print("  JC_Hardening_ABNM =", abnm)
    print("  Strain_Rate_Hardening_Coefficient =", c_val)
    print("  chip_thickness (Distance Minimale) =", chip_val)
    print("  Contact_Length (Distance entre le premier…) =", contact_val)

    print("\n✏️  Updating Chip project files…")
    patch_chip(tq, abnm, c_val, chip_val)

    print("\n✏️  Updating Contact_Length project files…")
    patch_contact(tq, abnm, c_val, contact_val)

    print("\n🎉  Done. Both projects are updated and JSON logs written.")

if __name__ == "__main__":
    main()
