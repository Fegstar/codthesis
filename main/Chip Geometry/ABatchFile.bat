@echo off
echo =============================================
echo  Launching Abaqus CAE (noGUI) – AExtractChip
echo =============================================

REM -- Run the Python extraction script ------------------------------
abaqus cae noGUI="C:\Users\ougbine\A\AExtractChip.py"

echo.
echo =============================================
echo  Script finished – press any key to exit
echo =============================================
pause
