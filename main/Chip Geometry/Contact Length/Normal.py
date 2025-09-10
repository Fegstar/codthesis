#!/usr/bin/env python3
import json
from pathlib import Path

# -------------------------------------------------------------------
# 1)  Paths to the two JSON files  – edit if the folder ever changes
# -------------------------------------------------------------------
contact_folder = Path(r"C:\Users\ougbine\Desktop\Contact_Length")
sens_file      = contact_folder / "sensitivity_results.json"
extr_file      = contact_folder / "extracted_values.json"

# -------------------------------------------------------------------
# 2)  Load both JSON files
# -------------------------------------------------------------------
with sens_file.open(encoding="utf-8") as f:
    sens = json.load(f)

with extr_file.open(encoding="utf-8") as f:
    ext = json.load(f)

# -------------------------------------------------------------------
# 3)  Gather the six material-property values
#     (Taylor-Quinney, 4 × JC_Hardening_ABNM, Strain-Rate-Hardening C)
# -------------------------------------------------------------------
# Strain-rate term might be a list [C] or already a scalar C
srh_raw = ext["Strain_Rate_Hardening_Coefficient"]
c_val   = srh_raw[0] if isinstance(srh_raw, list) else srh_raw

material_vals = [
    ext["Taylor_Quinney"],
    *ext["JC_Hardening_ABNM"][:4],   # first four values only
    c_val
]

# -------------------------------------------------------------------
# 4)  Pick Sensitivity_Parameter_2 … _7
# -------------------------------------------------------------------
sens_keys   = [f"Sensitivity_Parameter_{i}" for i in range(2, 8)]
sens_values = [sens[k] for k in sens_keys]

# -------------------------------------------------------------------
# 5)  Normalise:  (Sᵢ · materialᵢ) / Contact_Length
#     Accept either “Contact_Length” or legacy “Contact_Length”
# -------------------------------------------------------------------
contact_length = (
    ext.get("Contact_Length") or
    ext.get("Contact_Length") or
    ext.get("contact_length")
)

if contact_length is None:
    raise KeyError(
        "Neither 'Contact_Length' nor 'Contact_Length' found "
        "in extracted_values.json"
    )

normalised = {
    k: (s_val * m_val)
    for k, s_val, m_val in zip(sens_keys, sens_values, material_vals)
}

# -------------------------------------------------------------------
# 6)  Display on screen
# -------------------------------------------------------------------
print("Normalised sensitivities\n" + "-"*30)
for k, v in normalised.items():
    print(f"{k:<25} {v: .6f}")

# -------------------------------------------------------------------
# 7)  Save to new JSON file
# -------------------------------------------------------------------
out_file = contact_folder / "normalised_sensitivities.json"
with out_file.open("w", encoding="utf-8") as f_out:
    json.dump(normalised, f_out, indent=4)

print(f"\nSaved normalised sensitivities to: {out_file}")
