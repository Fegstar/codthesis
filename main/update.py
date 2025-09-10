#!/usr/bin/env python3
import re
import os
import sys
import json

def update_function_script(function_script_path, inelastic_params, plastic_params, rate_params):
    """
    Replaces only the lines in Function_Script.py that define:
        new_inelastic_params = "..."
        new_plastic_params   = "..."
        new_rate_params      = "..."
    with the new values while preserving the original indentation.
    """
    if not os.path.exists(function_script_path):
        print(f"[ERROR] {function_script_path} not found!")
        return False

    # Patterns to capture the entire lines with leading whitespace.
    pattern_inelastic = re.compile(r'^(\s*)new_inelastic_params\s*=\s*["\'].*["\']', re.MULTILINE)
    pattern_plastic   = re.compile(r'^(\s*)new_plastic_params\s*=\s*["\'].*["\']', re.MULTILINE)
    pattern_rate      = re.compile(r'^(\s*)new_rate_params\s*=\s*["\'].*["\']', re.MULTILINE)

    with open(function_script_path, 'r', encoding="utf-8") as f:
        content = f.read()

    # Replace lines while preserving indentation.
    new_content = pattern_inelastic.sub(r'\1new_inelastic_params = "' + inelastic_params + r'"', content)
    new_content = pattern_plastic.sub(r'\1new_plastic_params = "' + plastic_params + r'"', new_content)
    new_content = pattern_rate.sub(r'\1new_rate_params = "' + rate_params + r'"', new_content)

    with open(function_script_path, 'w', encoding="utf-8") as f:
        f.write(new_content)

    print("[OK] Updated new_inelastic_params, new_plastic_params, and new_rate_params in Function_Script.py")
    return True

def main():
    # Path to finals parameter JSON file (make sure it exists with the expected name).
    final_params_path = r"C:\Users\ougbine\Desktop\Chip\finals_param.json"
    function_script_path = r"C:\Users\ougbine\Function_Script.py"

    if not os.path.exists(final_params_path):
        print("[ERROR] Final parameters file not found!")
        sys.exit(1)

    with open(final_params_path, 'r', encoding="utf-8") as f:
        final_params = json.load(f)

    if not isinstance(final_params, list) or len(final_params) != 6:
        print(f"[ERROR] Expected 6 parameters in finals_param.json, but got {len(final_params)}.")
        sys.exit(1)

    # Split parameters:
    #   inelastic: first parameter
    #   plastic: next four parameters
    #   rate: last parameter
    inelastic_list = final_params[0:1]
    plastic_list   = final_params[1:5]
    rate_list      = final_params[5:6]

    # Format each list as a comma-separated string with six-decimal precision.
    inelastic_str = ", ".join(f"{v:.6f}" for v in inelastic_list)
    plastic_str   = ", ".join(f"{v:.6f}" for v in plastic_list)
    rate_str      = ", ".join(f"{v:.6f}" for v in rate_list)

    if update_function_script(function_script_path, inelastic_str, plastic_str, rate_str):
        print("Final parameters have been sent (updated) to Function_Script.py.")
        print("New inelastic parameters:", inelastic_str)
        print("New plastic parameters:", plastic_str)
        print("New rate parameters:   ", rate_str)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()