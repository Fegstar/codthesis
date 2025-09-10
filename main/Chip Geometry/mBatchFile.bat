@echo off
echo =============================================
echo  Launching Abaqus CAE (noGUI) – mExtractChip
echo =============================================

REM -- Run the Python extraction script ------------------------------
abaqus cae noGUI="C:\Users\ougbine\m\mExtractChip.py"

echo.
echo =============================================
echo  Script finished – press any key to exit
echo =============================================
pause
