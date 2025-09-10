#!/usr/bin/env python3
"""
norm_pforce.py  –  Normalised sensitivity calculator for P‑Force results
=======================================================================

This script mirrors *norm.py* (used for contact‑length studies) but adapts the
calculation for *passive force* (F₁ ≡ **force_p**) instead of contact length.

Given two JSON files:

1. **sensitivity_results.json**  – raw partial derivatives
   ( ∂F₁/∂xᵢ for the six material parameters )
2. **Pextracted.json**           – the material parameters themselves **and**
   the base output value `force_p` (F₁)

it computes the **normalised sensitivities**

               ∂F₁           xᵢ
    Sᵢⁿ = ────────  · ────────
                ∂xᵢ          F₁

for each parameter xᵢ ∈ {TQ,   A,   B,   n,   m,   C}
                    Taylor‑  JC‑  JC‑  JC‑  JC‑  Strain‑rate
                    Quinney  A    B    n    m    C

The resulting six numbers are printed and saved as
`normalised_sensitivities.json` alongside *sensitivity_results.json*.

Edit the three PATH variables below if your folder layout ever changes.
"""

import json
from pathlib import Path

# ────────────────────────────────────────────────────────────────────────
# 1)  Paths to the required JSON files  – adjust if your folders move
# ────────────────────────────────────────────────────────────────────────
pforce_folder = Path(r"C:\Users\ougbine\Desktop\PForce")
SENS_PATH     = pforce_folder / "sensitivity_results.json"
EXTRACT_PATH  = Path(r"C:\Users\Ougbine\Pextracted.json")

# ────────────────────────────────────────────────────────────────────────
# 2)  Load both JSON documents
# ────────────────────────────────────────────────────────────────────────
with SENS_PATH.open(encoding="utf-8") as f:
    sens_raw = json.load(f)

with EXTRACT_PATH.open(encoding="utf-8") as f:
    ext = json.load(f)

# ────────────────────────────────────────────────────────────────────────
# 3)  Gather the six material‑property values in the correct order
#     (TQ, A, B, n, m, C)
# ────────────────────────────────────────────────────────────────────────
try:
    tq_val  = float(ext["TQ"])  # Taylor‑Quinney
    a_val, b_val, n_val, m_val = [float(x) for x in ext["ABNM"][:4]]
except (KeyError, ValueError) as err:
    raise SystemExit(f"[ERROR] Missing or malformed ABNM/TQ fields: {err}")

# Strain‑rate term (C) can be scalar or a one‑item list – accept both
sr_raw = ext.get("rate_param") or ext.get("Strain_Rate_Hardening_Coefficient")
if sr_raw is None:
    raise SystemExit("[ERROR] Could not find 'rate_param' or 'Strain_Rate_Hardening_Coefficient' in Pextracted.json")

c_val = sr_raw[0] if isinstance(sr_raw, (list, tuple)) else float(sr_raw)

material_vals = [tq_val, a_val, b_val, n_val, m_val, c_val]

# ────────────────────────────────────────────────────────────────────────
# 4)  Extract the six matching sensitivity derivatives
#     (Sensitivity_Parameter_2 … 7)
# ────────────────────────────────────────────────────────────────────────
sens_keys   = [f"Sensitivity_Parameter_{i}" for i in range(2, 8)]
try:
    sens_values = [float(sens_raw[k]) for k in sens_keys]
except KeyError as err:
    raise SystemExit(f"[ERROR] Missing key in sensitivity_results.json: {err}")

# ────────────────────────────────────────────────────────────────────────
# 5)  Base output: the passive force F₁
# ────────────────────────────────────────────────────────────────────────
try:
    force_p = float(ext["force_p"])
except KeyError:
    raise SystemExit("[ERROR] 'force_p' not found in Pextracted.json")

if force_p == 0:
    raise SystemExit("[ERROR] force_p is zero – cannot normalise sensitivities.")

# ────────────────────────────────────────────────────────────────────────
# 6)  Compute the normalised sensitivities
# ────────────────────────────────────────────────────────────────────────
normalised = {
    k: (s_val * m_val)
    for k, s_val, m_val in zip(sens_keys, sens_values, material_vals)
}

# ────────────────────────────────────────────────────────────────────────
# 7)  Display on screen
# ────────────────────────────────────────────────────────────────────────
print("Normalised sensitivities (P‑Force)\n" + "-"*40)
for k, v in normalised.items():
    print(f"{k:<25} {v: .6f}")

# ────────────────────────────────────────────────────────────────────────
# 8)  Persist the results
# ────────────────────────────────────────────────────────────────────────
out_path = pforce_folder / "normalised_sensitivities.json"
with out_path.open("w", encoding="utf-8") as f_out:
    json.dump(normalised, f_out, indent=4)

print(f"\nSaved normalised sensitivities to: {out_path}")
