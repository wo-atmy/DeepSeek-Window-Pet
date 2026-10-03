@echo off
rem Stop the pet using the pid file it writes on startup.
rem ASCII-only on purpose (see launcher for why).
cd /d "%~dp0"

if not exist "pet.pid" (
  echo pet.pid not found - the pet does not look like it is running.
  pause
  exit /b 1
)

set /p PID=<"pet.pid"
echo Stopping pet, PID %PID% ...
taskkill /PID %PID% /F
del "pet.pid" 2>nul
timeout /t 2 >nul
