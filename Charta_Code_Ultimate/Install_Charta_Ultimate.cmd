@echo off
setlocal
cd /d "%~dp0"
python install.py
if %errorlevel% neq 0 pause
