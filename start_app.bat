@echo off
cd /d "%~dp0"
echo Starting SCDO Services...
echo.

echo Starting Backend Server...
start "SCDO Backend" cmd /k "venv\Scripts\activate && cd webapp\backend && python main.py"

echo Starting Frontend Dev Server...
start "SCDO Frontend" cmd /k "cd webapp\frontend && npm run dev"

echo.
echo Services started in new windows.
