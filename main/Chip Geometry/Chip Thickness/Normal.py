import json
from pathlib import Path

# -------------------------------------------------------------------
# 1)  Paths to your two JSON files  ― adapt if your folders change
# -------------------------------------------------------------------
chip_folder = Path(r"C:\Users\ougbine\Desktop\Chip")
sens_file   = chip_folder / "sensitivity_results.json"
extr_file   = chip_folder / "extracted_values.json"

# -------------------------------------------------------------------
# 2)  Load the data
# -------------------------------------------------------------------
with open(sens_file, "r") as f:
    sens = json.load(f)

with open(extr_file, "r") as f:
    ext  = json.load(f)

# -------------------------------------------------------------------
# 3)  Gather the six material‑property values
#     (Taylor‑Quinney, 4× JC_Hardening_ABNM, Strain‑Rate‑Hardening)
# -------------------------------------------------------------------
material_vals = [
    ext["Taylor_Quinney"],
    *ext["JC_Hardening_ABNM"],             # expands the 4‑element list
    ext["Strain_Rate_Hardening_Coefficient"][0]
]

# -------------------------------------------------------------------
# 4)  Pick Sensitivity_Parameter_2 … _7
# -------------------------------------------------------------------
sens_keys   = [f"Sensitivity_Parameter_{i}" for i in range(2, 8)]
sens_values = [sens[k] for k in sens_keys]

# -------------------------------------------------------------------
# 5)  Normalise:   (S_i  ·  material_i)
# -------------------------------------------------------------------
chip_thickness = ext["chip_thickness"]

norm = {
    k: (s_val * JC_val)
    for k, s_val, JC_val in zip(sens_keys, sens_values, material_vals)
}

# -------------------------------------------------------------------
# 6)  Show the results on screen
# -------------------------------------------------------------------
print("Normalised sensitivities\n" + "-"*30)
for k, v in norm.items():
    print(f"{k:<25} {v: .6f}")

# -------------------------------------------------------------------
# 7)  Save them to a new JSON file
# -------------------------------------------------------------------
norm_file = chip_folder / "normalised_sensitivities.json"
with open(norm_file, "w") as f_out:
    json.dump(norm, f_out, indent=4)

print(f"\nSaved normalised sensitivities to: {norm_file}")
