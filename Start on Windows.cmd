@echo off
setlocal
cd /d "%~dp0"
py -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1
if not errorlevel 1 (
  py -m travel_kit start
  goto :finished
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1
if not errorlevel 1 (
  python -m travel_kit start
  goto :finished
)
echo Install Python 3.11 or newer from https://www.python.org/downloads/ and try again.
pause
exit /b 1
:finished
if errorlevel 1 (
  echo The editor could not start. See docs\SETUP.md.
  pause
  exit /b 1
)
endlocal
