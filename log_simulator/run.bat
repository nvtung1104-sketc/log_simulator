@echo off
REM Simple launcher for Windows: double-click to create venv (if needed), install deps and run app

SETLOCAL

if not exist ".venv\Scripts\Activate.bat" (
  echo Creating virtual environment...
  python -m venv .venv
)

call ".venv\Scripts\Activate.bat"

if exist requirements.txt (
  echo Installing requirements...
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
)

echo Starting Log Generator Simulator (http://127.0.0.1:5000)...
python app.py --host=127.0.0.1 --port=5000

echo.
echo Server stopped. Press any key to close.
pause >nul
ENDLOCAL