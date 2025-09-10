#!/usr/bin/env python3
"""
update_force_scripts.py
----------------------------------------------------
Read `forceext.json`, update the hard‑coded constants scattered across the
C‑Force and P‑Force helper scripts, **show a live summary on the terminal**, and
write the whole set of fresh values + bookkeeping info to **Proforce.json**.

*New in this version*
---------------------
Besides the consolidated *Proforce.json* report, the script now also
creates two focused extracts that still include **all other parameters**
but carry only the relevant force component each – handy if a downstream
utility needs all modelling constants without parsing the big file:

* **Cextracted.json** → all parameters *except* `force_p`
* **Pextracted.json** → all parameters *except* `force_c`

Example (Cextracted.json)
```
{
    "force_c": 1234.56789,
    "TQ": 0.9,
    "ABNM": [880.0, 0.84, 0.001, 0.05],
    "rate_param": 0.015
}
```
Mappings applied
----------------
*   force_c          →  Cutting_Force (CFgradient.py) & Sim_Cutting_Force (CFError_…)
*   force_p          →  Passive_Force (PFgradient.py) & Sim_Passive_Force (PFError_…)
*   inelastic_params →  Taylor_Quinney
*   plastic_params   →  JC_Hardening_ABNM  (list of four floats)
*   rate_params      →  Strain_Rate_Hardening_Coefficient  (single‑item list)

A timestamped ***.bak*** copy of every target file is created the first time
it is modified, so you can roll back easily.
"""

import json, re, shutil, datetime, sys, traceback
from pathlib import Path

# ───────────────────────────────────────────────────────────────────────────────
# CONFIG – adjust only if your paths move
# ───────────────────────────────────────────────────────────────────────────────
JSON_PATH = Path(r"C:\Users\Ougbine\forceext.json")

C_GRADIENT = Path(r"C:\Users\ougbine\Desktop\CForce\CFgradient.py")
C_ERROR    = Path(r"C:\Users\ougbine\Desktop\CForce\CFError_Calculation.py")

P_GRADIENT = Path(r"C:\Users\ougbine\Desktop\PForce\PFgradient.py")
P_ERROR    = Path(r"C:\Users\ougbine\Desktop\PForce\PFError_Calculation.py")

OUT_JSON      = JSON_PATH.parent / "Proforce.json"     # C:\Users\Ougbine\Proforce.json
CEXTRACT_JSON = JSON_PATH.parent / "Cextracted.json"   # C:\Users\Ougbine\Cextracted.json
PEXTRACT_JSON = JSON_PATH.parent / "Pextracted.json"   # C:\Users\Ougbine\Pextracted.json
# ───────────────────────────────────────────────────────────────────────────────


def load_source_values(json_path: Path) -> dict:
    """Load numbers from *forceext.json* into a tidy dict of floats / lists."""
    data = json.loads(json_path.read_text())

    def parse_csv(csv: str):
        return [float(x) for x in csv.replace(";", ",").split(",") if x.strip()]

    return {
        "force_c":    float(data["force_c"]),
        "force_p":    float(data["force_p"]),
        "TQ":         float(data["inelastic_params"]),
        "ABNM":       parse_csv(data["plastic_params"]),       # 4 values
        "rate_param": float(data["rate_params"]),
    }


# ───────────────────────────── helper utils ──────────────────────────────


def backup_once(path: Path) -> None:
    """Make a one‑time *.bak* copy preserving mtime/ctime."""
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(path, bak.with_suffix(bak.suffix + f".{ts}"))
        print(f"[+] Backup created → {bak}")


def patch_file(path: Path, subs: dict) -> bool:
    """Patch assignment lines specified in *subs*. Return *True* if modified."""
    src_lines = path.read_text().splitlines()
    changed = False

    for idx, line in enumerate(src_lines):
        for var, new_rhs in subs.items():
            if re.match(rf"\s*{re.escape(var)}\s*=", line):
                indent = re.match(r"(\s*)", line).group(1)
                src_lines[idx] = f"{indent}{var} = {new_rhs}"
                changed = True
                break  # each line gets only one substitution

    if changed:
        backup_once(path)
        path.write_text("\n".join(src_lines), newline="\n")
        print(f"[✓] Patched {path.name}")
    else:
        print(f"[!] {path.name} – no matching lines found (nothing changed)")

    return changed


# ─────────────────────────────── main logic ──────────────────────────────


def main() -> None:
    print("\n=== Pro‑Force update utility ===\n")
    vals = load_source_values(JSON_PATH)

    # Pretty echo to the terminal ------------------------------------------------
    print("Extracted values from forceext.json:")
    print(f"  force_c          = {vals['force_c']:.6f}")
    print(f"  force_p          = {vals['force_p']:.6f}")
    print(f"  Taylor_Quinney   = {vals['TQ']:.6f}")
    print(f"  JC_Hardening_ABNM= {vals['ABNM']}")
    print(f"  rate_param       = {vals['rate_param']:.6f}\n")

    changed_files = []

    # C‑Force scripts ------------------------------------------------------------
    if patch_file(C_GRADIENT, {
        "Taylor_Quinney": f"{vals['TQ']:.6f}",
        "JC_Hardening_ABNM": str(vals["ABNM"]),
        "Strain_Rate_Hardening_Coefficient": f"[{vals['rate_param']:.6f}]",
        "Cutting_Force": f"{vals['force_c']:.6f}",
    }):
        changed_files.append(C_GRADIENT)

    if patch_file(C_ERROR, {
        "Sim_Cutting_Force": f"{vals['force_c']:.6f}",
    }):
        changed_files.append(C_ERROR)

    # P‑Force scripts ------------------------------------------------------------
    if patch_file(P_GRADIENT, {
        "Taylor_Quinney": f"{vals['TQ']:.6f}",
        "JC_Hardening_ABNM": str(vals["ABNM"]),
        "Strain_Rate_Hardening_Coefficient": f"[{vals['rate_param']:.6f}]",
        "Passive_Force": f"{vals['force_p']:.6f}",
    }):
        changed_files.append(P_GRADIENT)

    if patch_file(P_ERROR, {
        "Sim_Passive_Force": f"{vals['force_p']:.6f}",
    }):
        changed_files.append(P_ERROR)

    # ---------------------------------------------------------------------------
    if changed_files:
        print("\nSummary – updated files:")
        for fp in changed_files:
            print(f"  • {fp}")
    else:
        print("\nSummary – no files needed changes.")

    # Write consolidated JSON report -------------------------------------------
    summary = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "source_json": str(JSON_PATH),
        "values": vals,
        "files_patched": [str(p) for p in changed_files],
    }
    OUT_JSON.write_text(json.dumps(summary, indent=4))
    print(f"\n[→] Report written to {OUT_JSON}")

    # Write force extracts ------------------------------------------------------
    c_extract = {k: v for k, v in vals.items() if k != "force_p"}
    p_extract = {k: v for k, v in vals.items() if k != "force_c"}

    CEXTRACT_JSON.write_text(json.dumps(c_extract, indent=4))
    PEXTRACT_JSON.write_text(json.dumps(p_extract, indent=4))
    print(f"[→] force_c extract   → {CEXTRACT_JSON}")
    print(f"[→] force_p extract   → {PEXTRACT_JSON}\n")

    print("All done ✔")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        sys.exit(f"\nERROR: {exc}\n")
