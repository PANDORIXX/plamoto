@echo off
REM PLAMOTO setup script for Windows

echo Starting PLAMOTO setup...

REM 1. Create Python virtual environment
IF NOT EXIST ".venv" (
    python -m venv .venv
    echo Virtual environment created at .venv
)

REM 2. Activate virtual environment and install dependencies
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Python dependencies installed.

REM 3. Create images directory if it doesn't exist
IF NOT EXIST "static\images" (
    mkdir static\images
)
echo Images directory ensured at static\images

REM 4. Optional: check if cloudflared is installed
where cloudflared >nul 2>nul
IF ERRORLEVEL 1 (
    echo Warning: cloudflared not found. Cloudflare Quick Tunnel won't work.
)

echo PLAMOTO setup complete. You can now run:
echo    call .venv\Scripts\activate
echo    python app.py
pause
