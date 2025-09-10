#!/usr/bin/env python3
import json

def compute_error(Ref_Passive_Force, Sim_Passive_Force):
    """
    Computes the relative error as a percentage:
        ε = ((Ref_Passive_Force - Sim_Passive_Force) / Ref_Passive_Force) * 100

    Parameters:
        Ref_Passive_Force  (float): Reference value.
        Sim_Passive_Force (float): The computed or updated value Y(x^(i+1)).

    Returns:
        float: The relative error in percentage.
    """
    if Ref_Passive_Force == 0:
        raise ValueError("Ref_Passive_Force must not be zero to avoid division by zero.")

    epsilon = ((Ref_Passive_Force - Sim_Passive_Force) / Ref_Passive_Force) * 100
    return epsilon

if __name__ == "__main__":
    Ref_Passive_Force = 192.064
    Sim_Passive_Force = 192.338799

    error = compute_error(Ref_Passive_Force, Sim_Passive_Force)
    message = f"The relative error is {error:.2f}%"
    print(message)
    
    # Prepare the output data as a dictionary.
    error_data = {
        "Ref_Passive_Force": Ref_Passive_Force,
        "Sim_Passive_Force": Sim_Passive_Force,
        "relative_error": error,
        "message": message
    }
    
    # Write the dictionary to error.json file.
    with open("error.json", "w") as json_file:
        json.dump(error_data, json_file, indent=4)
    
    print("The error has also been saved to C:\\Users\\ougbine\\Desktop\\PForce\\error.json")