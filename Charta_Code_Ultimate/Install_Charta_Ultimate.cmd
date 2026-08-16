@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

:: Deteksi Python 3 yang tersedia
set "PYTHON="
for %%P in (python python3 py) do (
    if not defined PYTHON (
        where %%P >nul 2>&1 && set "PYTHON=%%P"
    )
)

if not defined PYTHON (
    echo [ERROR] Python 3 tidak ditemukan di PATH.
    echo Silakan install Python 3 dari https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Menggunakan Python: %PYTHON%
"%PYTHON%" install.py
if %errorlevel% neq 0 pause
