@echo off
echo =============================================
echo  Launching Abaqus CAE (noGUI) – nExtractChip
echo =============================================

REM -- Run the Python extraction script ------------------------------
abaqus cae noGUI="C:\Users\ougbine\n\nExtractChip.py"

echo.
echo =============================================
echo  Script finished – press any key to exit
echo =============================================
pause
