import os
import subprocess

def process_inp_file(input_filename, output_filename,
                     new_inelastic_params=None,
                     new_plastic_params=None,
                     new_rate_params=None):
    """
    Reads an Abaqus INP file, detects the sections for Inelastic, plasticity,
    and rate dependency (using the Johnson Cook keywords), and writes a modified file.
    
    For the plastic and rate blocks, only the first N comma-separated values are replaced,
    where N is the number of values provided in new_plastic_params or new_rate_params.
    The remaining original values are preserved.
    """
    if not os.path.isfile(input_filename):
        raise FileNotFoundError(f"Input file '{input_filename}' not found. Please check the file path.")

    with open(input_filename, "r") as infile:
        lines = infile.readlines()

    # Patterns to search for (case-insensitive)
    inelastic_keyword = "*Inelastic Heat Fraction"
    plastic_keyword   = "*Plastic, hardening=JOHNSON COOK"
    rate_keyword      = "*Rate Dependent, type=JOHNSON COOK"

    output_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Inelastic block (fully replace the next line)
        if inelastic_keyword.lower() in line.lower():
            output_lines.append(line)
            if i + 1 < len(lines):
                original_inelastic = lines[i+1].strip()
                if new_inelastic_params is not None:
                    print("Changing inelastic parameters:")
                    print("  Original:", original_inelastic)
                    print("  New:     ", new_inelastic_params)
                    output_lines.append(new_inelastic_params + "\n")
                else:
                    output_lines.append(lines[i+1])
            i += 2
            continue
        # Plasticity block (replace only the first N values)
        elif plastic_keyword.lower() in line.lower():
            output_lines.append(line)
            if i + 1 < len(lines):
                original_plastic = lines[i+1].strip()
                if new_plastic_params is not None:
                    original_parts = [p.strip() for p in original_plastic.split(',') if p.strip()]
                    new_parts = [p.strip() for p in new_plastic_params.split(',') if p.strip()]
                    count_replace = len(new_parts)
                    if count_replace < len(original_parts):
                        new_line_parts = new_parts + original_parts[count_replace:]
                    else:
                        new_line_parts = new_parts
                    new_line = ', '.join(new_line_parts) + ","
                    print("Changing plastic parameters:")
                    print("  Original:", original_plastic)
                    print("  New:     ", new_line)
                    output_lines.append(new_line + "\n")
                else:
                    output_lines.append(lines[i+1])
            i += 2
            continue
        # Rate dependency block (replace only the first N values)
        elif rate_keyword.lower() in line.lower():
            output_lines.append(line)
            if i + 1 < len(lines):
                original_rate = lines[i+1].strip()
                if new_rate_params is not None:
                    original_parts = [p.strip() for p in original_rate.split(',') if p.strip()]
                    new_parts = [p.strip() for p in new_rate_params.split(',') if p.strip()]
                    count_replace = len(new_parts)
                    if count_replace < len(original_parts):
                        new_line_parts = new_parts + original_parts[count_replace:]
                    else:
                        new_line_parts = new_parts
                    new_line = ', '.join(new_line_parts) + ","
                    print("Changing rate dependency parameters:")
                    print("  Original:", original_rate)
                    print("  New:     ", new_line)
                    output_lines.append(new_line + "\n")
                else:
                    output_lines.append(lines[i+1])
            i += 2
            continue
        else:
            output_lines.append(line)
            i += 1

    with open(output_filename, "w") as outfile:
        outfile.writelines(output_lines)
    print(f"Modified file written to {output_filename}")

def run_abaqus_job(inp_file, job_name, cpus=1, memory='2GB'):
    """
    Submits an Abaqus job using the given INP file and specified job name.
    """
    if not os.path.isfile(inp_file):
        raise FileNotFoundError(f"Cannot find INP file '{inp_file}' to run.")

    command = (
        f"abaqus job={job_name} "
        f"input=\"{inp_file}\" "
        f"cpus={cpus} "
        f"memory={memory} "
        f"interactive"
    )

    print("\nSubmitting the Abaqus job with command:")
    print(command)

    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Abaqus job '{job_name}' failed with return code {result.returncode}.")

    print(f"\nAbaqus job '{job_name}' completed successfully.")
    print(f"Check for '{job_name}.odb' in the same directory.")

if __name__ == "__main__":
    # These variable definitions are what update.py will update.
    new_inelastic_params = "0.948820"
    new_plastic_params = "1069.572082, 720.362473, 0.561582, 0.828054"
    new_rate_params = "0.041972"

    # Paths to the original and modified INP files.
    input_file  = "C:\\Users\\ougbine\\Href.inp"
    output_file = "C:\\Users\\ougbine\\Href_modified.inp"

    # Abaqus job settings.
    job_name      = "Yil"   # The ODB will be named 'code.odb'
    cpus_used     = 4
    memory_amount = "4GB"

    # Step 1: Modify the INP file with the new parameters.
    process_inp_file(
        input_file,
        output_file,
        new_inelastic_params=new_inelastic_params,
        new_plastic_params=new_plastic_params,
        new_rate_params=new_rate_params
    )

    # Step 2: Submit the modified INP as an Abaqus job.
    run_abaqus_job(
        inp_file=output_file,
        job_name=job_name,
        cpus=cpus_used,
        memory=memory_amount
    )
