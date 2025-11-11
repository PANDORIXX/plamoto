#!/bin/bash
# PLAMOTO setup script
# -------------------------------------------
# This script sets up the Python environment,
# installs dependencies, and ensures directories.
# Database migrations are NOT automatically run.
# -------------------------------------------

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting PLAMOTO setup..."

# -------------------------------------------
# 1. Create Python virtual environment
# -------------------------------------------
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Virtual environment created at .venv"
else
    echo "ℹ️  Virtual environment already exists."
fi

# -------------------------------------------
# 2. Activate virtual environment and install dependencies
# -------------------------------------------
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed."

# -------------------------------------------
# 3. Create required directories
# -------------------------------------------
mkdir -p static/images
echo "✅ Images directory ensured at static/images"

# -------------------------------------------
# 4. Check for cloudflared (optional)
# -------------------------------------------
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️  cloudflared not found. Cloudflare Quick Tunnel won't work."
else
    echo "✅ cloudflared is installed."
fi

# -------------------------------------------
# 5. Instructions for next steps
# -------------------------------------------
echo "-------------------------------------------"
echo "✅ PLAMOTO setup complete!"
echo "Next steps:"
echo "  1️⃣  Activate the virtual environment:"
echo "       source .venv/bin/activate"
echo "  2️⃣  Create your PostgreSQL database manually:"
echo "       sudo -u postgres psql"
echo "       CREATE ROLE plamoto_user WITH LOGIN PASSWORD 'yourpassword';"
echo "       ALTER ROLE plamoto_user CREATEDB;"
echo "       CREATE DATABASE plamoto OWNER plamoto_user;"
echo "       \\q"
echo "  3️⃣  Run database migrations:"
echo "       ./db_setup.sh"
echo "  4️⃣  Start the app:"
echo "       flask run"
echo "-------------------------------------------"