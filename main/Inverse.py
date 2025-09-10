#!/usr/bin/env python3
"""
Bound-constrained inverse identification (normalised version)
=============================================================
Works in the space of *relative* parameters  x̃ = x / x0.
A Gauss–Newton step is cast as a bound-constrained QP.

Dependencies
------------
    python -m pip install "qpsolvers[cvxopt]"
"""
from pathlib import Path
import json
import numpy as np
import qpsolvers as qp


# ───────────────────────── helper I/O ─────────────────────────────
def load_json(p: Path):
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(obj, p: Path):
    with p.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=4)


# ───────────────────── paths (edit if they change) ────────────────
base_dir = Path(r"C:\Users\ougbine")
chip_dir = base_dir / "Desktop" / "Chip"

# ────────────────────────── load data ─────────────────────────────
x_old_data        = load_json(chip_dir / "extracted_values.json")
numerical_vals    = np.array(load_json(base_dir / "sensitivity_param1.json"))
jacobian_original = np.array(load_json(base_dir / "sensitivity_matrix.json"))
experimental_vals = np.array([0.396586993740339, 0.314197, 621.397, 192.064])

# ───────────── current physical parameters  x0  (length 6) ───────
x0 = np.array([
    x_old_data["Taylor_Quinney"],
    *x_old_data["JC_Hardening_ABNM"],
    x_old_data["Strain_Rate_Hardening_Coefficient"][0],
])

# ─────────────── hard physical bounds (same order as x0) ──────────
LB_phys = np.array([0.60,  400.00, 100.00, 0.05, 0.2, 0.005])
UB_phys = np.array([0.95, 1100.00, 800.00, 0.80, 0.9, 0.900])

# ───────────────────── 1) Jacobian in normalised space ────────────
#   J_norm_ij = (∂F_j / ∂x_i) · x_i0   ––> multiply each column
J = jacobian_original            # broadcasting (n_out × 6)

# ───────────────────── 2) residual vector  F  (unchanged) ─────────
F = experimental_vals - numerical_vals

# ───────────────────── 3) bounds on Δx̃ (normalised step) ─────────
lb_delta = (LB_phys - x0) / x0        # (LB − x0)/x0
ub_delta = (UB_phys - x0) / x0

# ───────────────────── 4) Gauss–Newton step as QP ─────────────────
lam = 1e-2                             # Tikhonov parameter
P = J.T @ J + lam * np.eye(J.shape[1]) # 6 × 6
q = -J.T @ F                           # 6-vector

try:
    delta_tilde = qp.solve_qp(
        P, q, lb=lb_delta, ub=ub_delta, solver="cvxopt"
    )
    if delta_tilde is None:
        raise ValueError("QP solver returned None (infeasible / num. issue)")
except Exception as err:
    print(f"[warning] bounded QP step failed → {err}. Using unclipped GN step.")
    delta_tilde = np.linalg.solve(P, -q)
    delta_tilde = np.clip(delta_tilde, lb_delta, ub_delta)

# ───────────────────── 5) convert step back to physical space ─────
delta_phys = delta_tilde * x0          # δx = δx̃ · x0
x_new      = np.clip(x0 + delta_phys, LB_phys, UB_phys)

# ──────────────────────────── output  ─────────────────────────────
# JSON on a single line
print(json.dumps(x_new.tolist()))

out_path = chip_dir / "finals_param.json"
save_json(x_new.tolist(), out_path)
print(f"Updated parameters saved to {out_path}")
