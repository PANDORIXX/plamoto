# PLAMOTO – Plant Monitoring

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

PLAMOTO is a web-based plant monitoring system for Raspberry Pi. It captures images of plants automatically at scheduled intervals or manually on demand. Supports Raspberry Pi Camera (Picamera2) and DroidCam MJPEG streams. Optionally, it can expose the web app externally via a Cloudflare Quick Tunnel.

---

## Features

* Manual & Automatic Capture – Take snapshots on demand or schedule automatic captures.
* Background Capture – Configurable intervals for periodic image capture.
* Dashboard – Web interface displaying the latest captured image and background status.
* Camera Support – Raspberry Pi Camera (Picamera2) or DroidCam MJPEG streams.
* External Access – Optional Cloudflare Quick Tunnel for remote access.
* Settings Management – Configure camera, interval, and AWB settings via the web UI.
* Logging – Full logging for debugging and monitoring.

---

## Requirements

* Python 3.11+
* Flask
* Flask-Migrate
* SQLAlchemy
* psycopg2 (for PostgreSQL)
* Cloudflared (optional, for external access)

All Python dependencies are listed in `requirements.txt`.

---

## Installation

Clone the repository and enter the directory:

```bash
git clone https://github.com/PANDORIXX/plamoto.git
cd plamoto
```

### Environment Setup

Run the setup script to create the Python virtual environment, install dependencies, and prepare directories:

* Linux/macOS:

```bash
./setup.sh
```

* Windows (CMD):

```bat
setup.bat
```

---

### Configure Environment Variables

Create a `.env` file in the project root with your database credentials and other settings:

```
DATABASE_URL=postgresql://plamoto_user:yourpassword@localhost/plamoto
FLASK_APP=app.py
FLASK_ENV=development
```

Replace `plamoto_user`, `yourpassword`, and database name with your actual credentials.

---

### Database Setup

Create the PostgreSQL database manually (only once):

```sql
sudo -u postgres psql
CREATE ROLE plamoto_user WITH LOGIN PASSWORD 'yourpassword';
ALTER ROLE plamoto_user CREATEDB;
CREATE DATABASE plamoto OWNER plamoto_user;
\q
```

Run the database migrations:

```bash
./db_setup.sh
```

This initializes the migrations directory (if not existing), creates migration scripts, and applies them to the database.

---

## Usage

Activate the virtual environment and start the app:

```bash
source .venv/bin/activate
flask run
```

Open your browser at [http://localhost:5000](http://localhost:5000) or the Cloudflare Quick Tunnel URL (if enabled).

---

## Dashboard

* Displays the latest captured image.
* Shows background capture status and next scheduled capture.
* Provides buttons for manual capture or toggling background capture.

---

## Settings

Adjust via `/settings`:

* Camera Source: `picam` or `droidcam`
* Background Capture Interval: Minutes between automatic captures
* DroidCam IP/Port: For DroidCam streaming
* PiCam AWB Mode: Auto White Balance mode for Raspberry Pi Camera

---

## Project Structure

```
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
├── requirements.txt       # Python dependencies
├── setup.sh               # Full environment setup script
├── db_setup.sh            # Database migrations script
└── .env.example           # Example environment variables file
```

---

## Cloudflare Quick Tunnel (Optional)

PLAMOTO can expose the local web app to the internet:

* Starts a daemon thread on app startup.
* Logs the public URL once available.
* Requires `cloudflared` installed.

---

## License

MIT License – see [LICENSE](LICENSE) for details.

---

## Author

PANDORIXX – Lead Developer & Maintainer

---

## Contributing

Contributions are welcome! Open issues or submit pull requests for new features, bug fixes, or improvements.

---

## Notes

* Tested on Raspberry Pi with Picamera2 and DroidCam streams.
* Designed for Python 3.11+ and Flask.
* Setup scripts are idempotent and can be safely rerun.