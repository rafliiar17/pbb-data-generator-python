@echo off
:: Check if running with administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges.
    net start MongoDB
) else (
    echo Requesting administrator privileges...
    :: Re-run the script with administrator privileges
    powershell -Command "Start-Process cmd -ArgumentList '/c net start MongoDB && python mongo_status.py' -Verb RunAs"
)

:: Optionally, wait for user input to view output before closing
pause
