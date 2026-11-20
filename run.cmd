@echo off
title ShortsLab
cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python setup_and_run.py
    goto :eof
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py -3 setup_and_run.py
    goto :eof
)

for %%v in (313 312 311 310) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe" setup_and_run.py
        goto :eof
    )
    if exist "%ProgramFiles%\Python%%v\python.exe" (
        "%ProgramFiles%\Python%%v\python.exe" setup_and_run.py
        goto :eof
    )
)

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" setup_and_run.py
    goto :eof
)

goto :no_python

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
