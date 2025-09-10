"""
combine_parameters.py

Combine sensitivity parameter values from different JSON result files into
matrix form for downstream optimisation.

Outputs
-------
- **sensitivity_param1.json** : flat list `[p1_chip, p1_contact_length, p1_CForce, p1_PForce]`.
- **sensitivity_matrix.json** : 4 × 6 list‑of‑lists with parameters 2–7 from
  each label in the same row order.

The script also dumps both structures to the console so you can visually
confirm the layout.
"""
import json
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration – adjust here if you move the folders or add new labels
# ---------------------------------------------------------------------------
LABELS = ["chip", "contact_length", "CForce", "PForce"]

BASE_DIRS = {
    "chip": Path(r"C:\Users\ougbine\Desktop\Chip"),
    "contact_length": Path(r"C:\Users\ougbine\Desktop\Contact_Length"),
    "CForce": Path(r"C:\Users\ougbine\Desktop\CForce"),
    "PForce": Path(r"C:\Users\ougbine\Desktop\PForce"),
}

SENS_FILE = "sensitivity_results.json"          # raw sensitivities (Parameter 1)
NORM_FILE = "normalised_sensitivities.json"     # normalised sensitivities (2–7)

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    """Safely load a JSON file, raising informative errors on failure."""
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)

# ---------------------------------------------------------------------------
# Part 1 – collect Parameter 1 into a flat list
# ---------------------------------------------------------------------------
print("\nCollecting Sensitivity_Parameter_1 …")
param1_values = []  # flat list → length 4
for label in LABELS:
    data = load_json(BASE_DIRS[label] / SENS_FILE)
    try:
        param1_values.append(float(data["Sensitivity_Parameter_1"]))
    except KeyError as exc:
        raise KeyError(f"'Sensitivity_Parameter_1' missing in {label}") from exc

with open("sensitivity_param1.json", "w", encoding="utf-8") as fp:
    json.dump(param1_values, fp, separators=(',', ':'))  # one‑dim list

# ---------------------------------------------------------------------------
# Part 2 – build the 4 × 6 matrix for parameters 2–7
# ---------------------------------------------------------------------------
print("Collecting Sensitivity_Parameters 2–7 …")
PARAM_KEYS = [f"Sensitivity_Parameter_{i}" for i in range(2, 8)]  # 2 → 7
matrix = []

for label in LABELS:
    data = load_json(BASE_DIRS[label] / NORM_FILE)
    row = []
    for key in PARAM_KEYS:
        try:
            row.append(float(data[key]))
        except KeyError as exc:
            raise KeyError(f"'{key}' missing in {label}") from exc
    matrix.append(row)

with open("sensitivity_matrix.json", "w", encoding="utf-8") as fp:
    json.dump(matrix, fp, separators=(',', ':'))

# ---------------------------------------------------------------------------
# User‑friendly console output (multi‑line for readability)
# ---------------------------------------------------------------------------
print("\nParameter 1 list (length {n}):".format(n=len(param1_values)))
print(param1_values)

print("\nSensitivity matrix (shape {r}×{c}):".format(r=len(matrix), c=len(PARAM_KEYS)))
for row in matrix:
    print(row)

print("\nDone! › Files written to: " + os.getcwd())
