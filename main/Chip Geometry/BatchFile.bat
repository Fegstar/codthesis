@echo off
echo ===========================================================================
echo    Launching both Abaqus scripts in parallel (no GUI) with parameter extract
echo ===========================================================================

setlocal enabledelayedexpansion

echo [Step 1/3] Extracting Johnson-Cook parameters from Function_Script.py...
REM -----------------------------------------------------------------------
REM  Find lines that define new_inelastic, new_plastic, new_rate at the start
REM  of the line. Split on '=' and remove double quotes.
REM  Adjust the file path if needed.
REM -----------------------------------------------------------------------

REM Extract new_inelastic
FOR /F "usebackq tokens=1,* delims== " %%A IN (`findstr /R /C:"^new_inelastic" "C:\\Users\\ougbine\\Function_Script.py"`) DO (
    set "temp=%%B"
    set temp=!temp:"=!
    set "new_inelastic=!temp!"
)

REM Extract new_plastic
FOR /F "usebackq tokens=1,* delims== " %%A IN (`findstr /R /C:"^new_plastic" "C:\\Users\\ougbine\\Function_Script.py"`) DO (
    set "temp=%%B"
    set temp=!temp:"=!
    set "new_plastic=!temp!"
)

REM Extract new_rate
FOR /F "usebackq tokens=1,* delims== " %%A IN (`findstr /R /C:"^new_rate" "C:\\Users\\ougbine\\Function_Script.py"`) DO (
    set "temp=%%B"
    set temp=!temp:"=!
    set "new_rate=!temp!"
)

echo   Found new_inelastic = %new_inelastic%
echo   Found new_plastic   = %new_plastic%
echo   Found new_rate      = %new_rate%
echo.

echo [Step 2/3] Starting Function_Script.py in parallel with no GUI...
start "Function_Script" abaqus cae noGUI="C:\\Users\\ougbine\\Function_Script.py"

echo [Step 3/3] Starting final_code_for_Chip.py in parallel with no GUI...
start "Final_Script" abaqus cae noGUI="C:\\Users\\ougbine\\final_code_for_Fegor.py"

echo ===========================================================================
echo Both scripts have been started in parallel.
echo You may close this window at any time or wait for each script's own window to close.
echo ===========================================================================
pause
endlocal
