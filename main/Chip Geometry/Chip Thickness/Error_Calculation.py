#!/usr/bin/env python3
import json

def compute_error(Ref_Chip, Sim_Chip):
    """
    Computes the relative error as a percentage:
        ε = ((Ref_Chip - Sim_Chi) / Ref_Chip) * 100

    Parameters:
        Ref_Chip  (float): Reference value.
        Sim_Chip (float): The computed or updated value Y(x^(i+1)).

    Returns:
        float: The relative error in percentage.
    """
    if Ref_Chip == 0:
        raise ValueError("Ref_Chip must not be zero to avoid division by zero.")

    epsilon = ((Ref_Chip - Sim_Chip) / Ref_Chip) * 100
    return epsilon

if __name__ == "__main__":
    Ref_Chip = 0.396586993740339
    Sim_Chip = 0.00707106781186548

    error = compute_error(Ref_Chip, Sim_Chip)
    message = f"The relative error is {error:.2f}%"
    print(message)
    
    # Prepare the output data as a dictionary.
    error_data = {
        "Ref_Chip": Ref_Chip,
        "Sim_Chip": Sim_Chip,
        "relative_error": error,
        "message": message
    }
    
    # Write the dictionary to error.json file.
    with open("error.json", "w") as json_file:
        json.dump(error_data, json_file, indent=4)
    
    print("The error has also been saved to C:\\Users\\ougbine\\Desktop\\Chip\\error.json")