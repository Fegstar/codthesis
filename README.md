# Inverse Identification for Machining (Abaqus + Python)

This repository provides scripts to extract chip geometry and forces from Abaqus ODB files and to run a Gauss-Newton update to identify Johnson-Cook material parameters.

## What it does
- Extract chip thickness and contact length from ODB
- Extract cutting force Fc and passive force Fp
- Build sensitivity data as JSON
- Solve a bound constrained Gauss-Newton step in relative parameter space
- Write updated Johnson-Cook parameters to an INP helper

## Repository layout
```
Coding/
├─ Chip Geometry/
│  ├─ AExtractChip.py
│  ├─ AProcessing.py
│  ├─ Chip Thickness/
│  │  ├─ Normal.py
│  │  ├─ Gradient.py
│  │  └─ Error_Calculation.py
│  └─ Contact Length/
│     ├─ Normal.py
│     ├─ Gradient.py
│     └─ Error_Calculation.py
├─ Force/
│  ├─ AEXTForce.py
│  ├─ Cutting Force/
│  └─ Penetration Force/
├─ Inverse.py
├─ Function_Script.py
├─ update.py
├─ combine.py
├─ *.inp
└─ Coding Flowchart.pdf
```

## Requirements
Two Python environments are typical.
1. System Python for data processing and inverse step
   - Python 3.9 or later
   - numpy
   - scipy
   - qpsolvers[cvxopt]
2. Abaqus Python for scripts that import odbAccess or abaqus modules
   - Abaqus installed with ODB API
   - Run with `abaqus python` or `abaqus cae noGUI=...`

### System Python setup
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS or Linux
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install numpy scipy "qpsolvers[cvxopt]"
```

## Configure paths
Some scripts contain absolute Windows paths. Replace them with repo relative paths or supply arguments.
Example locations to update:
- Force/AEXTForce.py default ODB path
- Any JSON output path constants

## Workflow
1. Place ODB files in `data/`
2. Extract chip geometry
   ```bat
   abaqus cae noGUI="Coding\Chip Geometry\AExtractChip.py"
   ```
3. Extract forces
   ```bat
   abaqus python "Coding\Force\EXTForce.py" -- -odb "data\AChipInp.odb"
   ```
4. Build sensitivities
   ```bash
   python Coding/combine.py
   ```
5. Run inverse update
   ```bash
   python Coding/Inverse.py
   ```
6. Update INP for next Abaqus run
   ```bash
   python Coding/Function_Script.py
   # or
   python Coding/update.py
   ```

## Inputs and outputs
Inputs
- Abaqus ODB files
- Template INP files containing Johnson-Cook blocks
- Experimental reference values for chip thickness, contact length, and forces

Key JSON outputs
- extracted_values.json for geometry
- Cextracted.json and Pextracted.json for forces
- normalised_sensitivities.json per metric
- sensitivity_param1.json and sensitivity_matrix.json for the inverse step
- finals_param.json with the next Johnson-Cook guess

## Troubleshooting
- ImportError no module named odbAccess
  - Run the script with Abaqus Python
- SciPy import fails inside Abaqus
  - Avoid SciPy in Abaqus scripts or install SciPy into Abaqus Python
- qpsolvers or cvxopt missing
  - Install with `python -m pip install "qpsolvers[cvxopt]"`
