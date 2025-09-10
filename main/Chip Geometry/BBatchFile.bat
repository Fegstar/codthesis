@echo off
echo =============================================
echo  Launching Abaqus CAE (noGUI) – BExtractChip
echo =============================================

REM -- Run the Python extraction script ------------------------------
abaqus cae noGUI="C:\Users\ougbine\B\BExtractChip.py"

echo.
echo =============================================
echo  Script finished – press any key to exit
echo =============================================
pause
