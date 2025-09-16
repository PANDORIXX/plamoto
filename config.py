class Config: 
    SETTINGS_FILE = 'settings.json'
    IMAGE_DIR = 'static/images'
    LOG_FILE = 'logs/plant_monitor.log'
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5000
    BACKGROUND_CAPTURE_MIN_INTERVAL = 1
    LOG_MAX_BYTES = 1 * 1024 * 1024
    LOG_BACKUP_COUNT = 2