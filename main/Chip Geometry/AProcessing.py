#!/usr/bin/env python3
r"""
combine_processing_conpro_index.py
──────────────────────────────────
Reads C:\Users\ougbine\abaqus.rpy and updates the chosen index (0-based) of:

  • Chip  → C:\Users\ougbine\Desktop\Chip\Gradient.py
      pet_chip_thickness[index]  ← last "Distance Minimale: <val>"

  • Contact_Length → C:\Users\ougbine\Desktop\Contact_Length\Gradient.py
      Pet_Contact_Length[index]  ← last "Distance entre le premier et le dernier point … : <val>"

Creates timestamped .bak.YYYYMMDD_HHMMSS backups before editing.
"""

from __future__ import annotations
import argparse, re, shutil, sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

DEFAULT_RPY          = Path(r"C:\Users\ougbine\abaqus.rpy")
DEFAULT_CHIP_GRAD    = Path(r"C:\Users\ougbine\Desktop\Chip\Gradient.py")
DEFAULT_CONTACT_GRAD = Path(r"C:\Users\ougbine\Desktop\Contact_Length\Gradient.py")

NUM_RE = r"[-+]?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?"
P_CHIP_LINE    = re.compile(r"Distance\s+Minimale\s*:\s*(?P<val>" + NUM_RE + r")", re.I)
P_CONTACT_LINE = re.compile(r"Distance\s+entre\s+le\s+premier.*dernier\s+point.*", re.I)

def _read_text_any(p: Path) -> str:
    for enc in ("utf-8", "cp1252", "latin-1"):
        try: return p.read_text(encoding=enc)
        except UnicodeDecodeError: continue
    return p.read_text(encoding="latin-1", errors="ignore")

def _to_float(s: str) -> float:
    return float(s.replace(",", "."))

def extract_distances(rpy: Path) -> Tuple[float,float]:
    txt = _read_text_any(rpy)
    chip_matches = list(P_CHIP_LINE.finditer(txt))
    if not chip_matches: sys.exit("❌ No 'Distance Minimale' found")
    chip_val = _to_float(chip_matches[-1].group("val"))
    contact_lines = [m.group(0) for m in P_CONTACT_LINE.finditer(txt)]
    if not contact_lines: sys.exit("❌ No French contact line found")
    nums = re.findall(NUM_RE, contact_lines[-1])
    if not nums: sys.exit("❌ No number found in contact line")
    contact_val = _to_float(nums[-1])
    return chip_val, contact_val

def backup_file(p: Path) -> Path:
    b = p.with_suffix(p.suffix + f".bak.{datetime.now():%Y%m%d_%H%M%S}")
    shutil.copy2(p, b); return b

def patch_list_elem(pyfile: Path, var_name: str, new_value: float, index: int) -> tuple[str,str]:
    src = _read_text_any(pyfile)
    pat = re.compile(rf"(^\s*{re.escape(var_name)}\s*=\s*\[)([^\]]*)(\])",
                     flags=re.MULTILINE | re.DOTALL)
    m = pat.search(src)
    if not m: sys.exit(f"❌ Could not locate list for '{var_name}' in {pyfile}")
    elems = [e.strip() for e in m.group(2).split(",")]
    if index >= len(elems): sys.exit(f"❌ Index {index} out of range for {var_name}")
    before, after = elems[index], f"{new_value:.6f}"
    elems[index] = after
    new_src = src[:m.start(2)] + ", ".join(elems) + src[m.end(2):]
    backup_file(pyfile)
    pyfile.write_text(new_src, encoding="utf-8")
    return before, after

def main():
    ap = argparse.ArgumentParser(description="Update Nth element of pet lists from Abaqus replay distances.")
    ap.add_argument("--index", type=int, default=1, help="0-based index to update (default=1 for second element)")
    ap.add_argument("--rpy",     default=str(DEFAULT_RPY))
    ap.add_argument("--chip",    default=str(DEFAULT_CHIP_GRAD))
    ap.add_argument("--contact", default=str(DEFAULT_CONTACT_GRAD))
    args = ap.parse_args()

    chip_val, contact_val = extract_distances(Path(args.rpy))
    print(f"Parsed: chip={chip_val:.6f}, contact={contact_val:.6f}")

    old,new = patch_list_elem(Path(args.chip), "pet_chip_thickness", chip_val, args.index)
    print(f"  pet_chip_thickness[{args.index}]: {old} → {new}")

    old,new = patch_list_elem(Path(args.contact), "Pet_Contact_Length", contact_val, args.index)
    print(f"  Pet_Contact_Length[{args.index}]: {old} → {new}")

    print("✅ Done (backups created).")

if __name__=="__main__":
    main()
