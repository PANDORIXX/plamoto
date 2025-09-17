#!/bin/bash
# PLAMOTO setup script

# Exit on error
set -e

echo "Starting PLAMOTO setup..."

# 1. Create Python virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created at .venv"
fi

# 2. Activate virtual environment and install dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Python dependencies installed."

# 3. Create images directory if it doesn't exist
mkdir -p static/images
echo "Images directory ensured at static/images"

# 4. Optional: check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "Warning: cloudflared not found. Cloudflare Quick Tunnel won't work."
fi

echo "PLAMOTO setup complete. You can now run:"
echo "  source .venv/bin/activate"
echo "  python app.py"
