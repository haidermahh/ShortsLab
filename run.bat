@echo off
title ShortsLab
cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% neq 0 goto :no_python

python setup_and_run.py
goto :eof

:no_python
echo.
echo ========================================================
echo   ERROR: Python is not installed or not found in PATH!
echo ========================================================
echo.
echo   Please download and install Python 3.10 or newer from:
echo   https://www.python.org/downloads/
echo.
echo   IMPORTANT: Make sure to check "Add python.exe to PATH"
echo   during Python installation!
echo.
pause
exit /b 1
