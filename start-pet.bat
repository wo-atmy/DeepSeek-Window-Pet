@echo off
rem Launch the whale pet without a console window.
rem Keep this file ASCII-only: cmd.exe reads .bat as ANSI/GBK,
rem so non-ASCII text here would be garbled.
cd /d "%~dp0"

where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw "whale_pet.py"
  exit /b
)

echo pythonw not found; falling back to python (a console window will stay open).
start "" python "whale_pet.py"
