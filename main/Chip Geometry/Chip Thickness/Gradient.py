#!/usr/bin/env python3
import json

# ------------------------------------------------------------------
# ①  If you really need another script to run beforehand, call it here
def run_sequential():
    print("Running sequential pre-processing (if any)…")
    # subprocess.run(["python", "sequential.py"])
# ------------------------------------------------------------------

def get_thickness_sensitivities(
    TQ, jc_ABNM, C,                     # Johnson–Cook inputs
    chip_thickness,                    # measured / reference thickness
    pet_chip_thickness_list,           # one entry per JC parameter
    eps=0.2                            # relative perturbation size
):
    """
    Returns a list whose first element is `chip_thickness`, followed by
    ∂h/∂pᵢ for every parameter pᵢ, each evaluated with its own
    `pet_chip_thickness_list[i]`.
    """

    # ----- 1) collect parameters in a flat list --------------------
    jc_params = [TQ] + jc_ABNM + C                 # 1 + 4 + 1 = 6 values
    if len(jc_params) != len(pet_chip_thickness_list):
        raise ValueError("pet_chip_thickness_list must match # of JC parameters")

    sensitivities = [chip_thickness]               # Sensitivity #1

    # ----- 2) loop parameter-by-parameter --------------------------
    for p_val, pet_h in zip(jc_params, pet_chip_thickness_list):
        dX = eps * p_val if p_val != 0 else eps    # avoid Δp = 0
        dh_dp = (pet_h - chip_thickness) / dX
        sensitivities.append(dh_dp)

    return sensitivities

def main():
    # -------------------- INPUTS --------------------
    Taylor_Quinney = 0.94882
    JC_Hardening_ABNM = [1069.572082, 720.362473, 0.561582, 0.828054]
    Strain_Rate_Hardening_Coefficient = [0.041972]
    chip_thickness = 0.00707106781186548

    # One pet-chip-thickness per parameter (TQ, A, B, N, M, C)
    pet_chip_thickness = [0.007071, 0.353279, 0.426485, 0.433780, 0.429040, 0.005000]

    # -------------------- RUN -----------------------
    run_sequential()

    sens = get_thickness_sensitivities(
        Taylor_Quinney,
        JC_Hardening_ABNM,
        Strain_Rate_Hardening_Coefficient,
        chip_thickness,
        pet_chip_thickness
    )

    print("\n✅  Compute Sensitivity")
    for i, s in enumerate(sens, 1):
        print(f"  Sensitivity Parameter #{i}: {s:.6f}")

    # -------------------- SAVE ----------------------
    out = {f"Sensitivity_Parameter_{i+1}": v for i, v in enumerate(sens)}
    with open(r"C:\Users\ougbine\Desktop\Chip\sensitivity_results.json", "w") as f:
        json.dump(out, f, indent=4)
    print("\n✅  Results written to sensitivity_results.json")

if __name__ == "__main__":
    main()