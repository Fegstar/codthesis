#!/usr/bin/env python3
"""
update_pet_forces.py
----------------------------------------------------
Read nForce.json and insert:
    • force_c -> first item of Pet_Cutting_Force   in CFgradient.py
    • force_p -> first item of Pet_Passive_Force  in PFgradient.py
"""

import json, re, shutil, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS — adjust if your folders ever move
# ---------------------------------------------------------------------------
nFORCE_JSON = Path(r"C:\Users\Ougbine\nForce.json")

CF_GRADIENT  = Path(r"C:\Users\ougbine\Desktop\CForce\CFgradient.py")
PF_GRADIENT  = Path(r"C:\Users\ougbine\Desktop\PForce\PFgradient.py")
# ---------------------------------------------------------------------------


def load_forces(json_path: Path) -> tuple[float, float]:
    """Return (force_c, force_p) from nForce.json."""
    data = json.loads(json_path.read_text())
    return float(data["force_c"]), float(data["force_p"])


def backup_once(path: Path) -> None:
    """Create a .bak copy (only once) with a timestamp."""
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(path, bak.with_suffix(bak.suffix + f".{ts}"))
        print(f"[+] Backup saved → {bak}")


def patch_first_value(path: Path, list_name: str, new_val: float) -> None:
    """
    Replace only the first element of the list assignment:
        list_name = [x0, x1, ...]
    keeping everything else identical (spacing, remaining numbers, comments).
    """
    src = path.read_text().splitlines()
    pat = re.compile(rf"^(\s*{re.escape(list_name)}\s*=\s*\[)([^\]]+)(\].*)$")

    for i, line in enumerate(src):
        m = pat.match(line)
        if m:
            # Split the RHS list elements by comma, keep original formatting
            elements = m.group(2).split(",")
            if not elements:
                raise ValueError(f"{list_name} appears empty in {path}")
            # Replace first element, preserving its original width / formatting
            elements[3] = f" {new_val:.6f}"  # leading space for readability
            new_rhs = ",".join(elements)
            src[i] = f"{m.group(1)}{new_rhs}{m.group(3)}"
            backup_once(path)
            path.write_text("\n".join(src), newline="\n")
            print(f"[✓] Updated {list_name}[0] in {path.name} → {new_val:.6f}")
            return

    print(f"[!] {list_name} not found in {path.name} (no changes)")


def main() -> None:
    force_c, force_p = load_forces(nFORCE_JSON)

    print(f"Loaded forces from {nFORCE_JSON}:")
    print(f"    force_c = {force_c:.6f}")
    print(f"    force_p = {force_p:.6f}\n")

    patch_first_value(CF_GRADIENT, "Pet_Cutting_Force",  force_c)
    patch_first_value(PF_GRADIENT, "Pet_Passive_Force",  force_p)

    print("\nAll done ✔")


if __name__ == "__main__":
    main()
