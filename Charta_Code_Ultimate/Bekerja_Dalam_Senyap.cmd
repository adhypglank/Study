@echo off
setlocal
cd /d "%~dp0"
python launch.py --senyap src/program.spok charta_output.cht
if %errorlevel% neq 0 pause
