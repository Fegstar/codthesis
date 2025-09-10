#!/usr/bin/env python3
import json

def compute_error(Ref_Cutting_Force, Sim_Cutting_Force):
    """
    Computes the relative error as a percentage:
        ε = ((Ref_Cutting_Force - Sim_Cutting_Force) / Ref_Cutting_Force) * 100

    Parameters:
        Ref_Cutting_Force  (float): Reference value.
        Sim_Cutting_Force (float): The computed or updated value Y(x^(i+1)).

    Returns:
        float: The relative error in percentage.
    """
    if Ref_Cutting_Force == 0:
        raise ValueError("Ref_Cutting_Force must not be zero to avoid division by zero.")

    epsilon = ((Ref_Cutting_Force - Sim_Cutting_Force) / Ref_Cutting_Force) * 100
    return epsilon

if __name__ == "__main__":
    Ref_Cutting_Force = 621.397
    Sim_Cutting_Force = 622.113895

    error = compute_error(Ref_Cutting_Force, Sim_Cutting_Force)
    message = f"The relative error is {error:.2f}%"
    print(message)
    
    # Prepare the output data as a dictionary.
    error_data = {
        "Ref_Cutting_Force": Ref_Cutting_Force,
        "Sim_Cutting_Force": Sim_Cutting_Force,
        "relative_error": error,
        "message": message
    }
    
    # Write the dictionary to error.json file.
    with open("error.json", "w") as json_file:
        json.dump(error_data, json_file, indent=4)
    
    print("The error has also been saved to C:\\Users\\ougbine\\Desktop\\CForce\\error.json")