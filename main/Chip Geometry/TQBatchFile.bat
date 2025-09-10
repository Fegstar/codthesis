@echo off
echo =============================================
echo  Launching Abaqus CAE (noGUI) – TQExtractChip
echo =============================================

REM -- Run the Python extraction script ------------------------------
abaqus cae noGUI="C:\Users\ougbine\TQ\TQExtractChip.py"

echo.
echo =============================================
echo  Script finished – press any key to exit
echo =============================================
pause
