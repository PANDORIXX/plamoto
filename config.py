import secrets
import os

class Config: 
    # Files and directories
    SETTINGS_FILE = 'config/settings.json'
    IMAGE_DIR = 'static/images'
    LOG_FILE = 'logs/plant_monitor.log'

    # Flask configuration
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5000
    SECRET_KEY = secrets.token_hex(32)

    # Logging configuration
    LOG_MAX_BYTES = 1 * 1024 * 1024
    LOG_BACKUP_COUNT = 2

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://plamoto_user:plamoto_pass@localhost:5432/plamoto_db" # Change as needed
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # General settings
    BACKGROUND_CAPTURE_MIN_INTERVAL = 1
    DEBUG = True
    CLOUDFLARE_ENABLED = False