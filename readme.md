# PLAMOTO – PLAnt MOniTOring

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)  
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

PLAMOTO is a web-based plant monitoring system designed for Raspberry Pi. It captures images of plants automatically at scheduled intervals or manually on demand. It supports both the Raspberry Pi Camera (Picamera2) and DroidCam streams. Optionally, it can expose the web app externally via a Cloudflare Quick Tunnel.

---

## Features

- **Manual & Automatic Capture** – Take snapshots on demand or schedule automatic captures.
- **Background Capture** – Configurable intervals for periodic image capture.
- **Dashboard** – Web interface displaying the latest captured image.
- **Camera Support** – Raspberry Pi Camera (Picamera2) or DroidCam MJPEG streams.
- **External Access** – Optional Cloudflare Quick Tunnel for remote access.
- **Settings Management** – Configure camera, interval, and AWB settings through the web UI.
- **Logging** – Full logging for debugging and monitoring.

---

## Installation

Clone the repository and set up a Python virtual environment:

```bash
git clone https://github.com/<your-username>/plamoto.git
cd plamoto
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
Edit config.py to configure:

IMAGE_DIR – folder where captured images are stored

SETTINGS_FILE – path for settings.json

Usage
Start the web app:

bash
Code kopieren
python app.py
Open your browser at http://localhost:5000.

Dashboard
Shows the latest captured image.

Displays background capture status and next scheduled capture.

Provides buttons to manually capture or toggle background capture.

Settings
Adjust via /settings:

Camera Source: 'picam' or 'droidcam'

Background Capture Interval: Minutes between automatic captures

DroidCam IP/Port: For DroidCam streaming

PiCam AWB Mode: Auto White Balance mode for Raspberry Pi Camera

Project Structure
php
Code kopieren
plamoto/
├── app.py                 # Main Flask application
├── camera.py              # Camera handling (Picamera2 & DroidCam)
├── settings.py            # Load, save, and parse settings
├── background_capture.py  # Background capture thread management
├── external_access.py     # Cloudflare Quick Tunnel logic
├── config.py              # Application constants
├── static/
│   └── images/            # Captured images
├── templates/             # HTML templates for web interface
└── requirements.txt       # Python dependencies
Cloudflare Quick Tunnel (Optional)
PLAMOTO can expose the local web app to the internet using Cloudflare Quick Tunnel:

Automatically starts a daemon thread on app startup.

Logs the public URL once available.

Requires cloudflared installed on your Raspberry Pi.

License
MIT License – see LICENSE file for details.

Author
Luca – Lead Developer & Maintainer

Contributing
Contributions are welcome! Please open issues or submit pull requests for new features, bug fixes, or improvements.

Notes
Tested on Raspberry Pi with Picamera2 and DroidCam streams.

Designed for Python 3.11+ and Flask.