#!/usr/bin/env python3
import json

def compute_error(Ref_Contact_Length, Sim_Contact_Length):
    """
    Computes the relative error as a percentage:
        ε = ((Ref_Contact_Length - Sim_Contact_Length) / Ref_Contact_Length) * 100

    Parameters:
        Ref_Contact_Length  (float): Reference value.
        Sim_Contact_Length (float): The computed or updated value Y(x^(i+1)).

    Returns:
        float: The relative error in percentage.
    """
    if Ref_Contact_Length == 0:
        raise ValueError("Ref_Contact_Length must not be zero to avoid division by zero.")

    epsilon = ((Ref_Contact_Length - Sim_Contact_Length) / Ref_Contact_Length) * 100
    return epsilon

if __name__ == "__main__":
    Ref_Contact_Length = 0.314197
    Sim_Contact_Length = 0.314197

    error = compute_error(Ref_Contact_Length, Sim_Contact_Length)
    message = f"The relative error is {error:.2f}%"
    print(message)
    
    # Prepare the output data as a dictionary.
    error_data = {
        "Ref_Contact_Length": Ref_Contact_Length,
        "Sim_Contact_Length": Sim_Contact_Length,
        "relative_error": error,
        "message": message
    }
    
    # Write the dictionary to error.json file.
    with open("error.json", "w") as json_file:
        json.dump(error_data, json_file, indent=4)
    
    print("The error has also been saved to C:\\Users\\ougbine\\Desktop\\Chip\\Contact_Length.json")