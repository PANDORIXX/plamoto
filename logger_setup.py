import logging
from logging.handlers import RotatingFileHandler
from config import Config

def setup_logger(name=None): 
    """Create and return a configured logger instance using Config."""
    if name is None: 
        name = "unknown"
        
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        Config.LOG_FILE, 
        maxBytes=Config.LOG_MAX_BYTES, 
        backupCount=Config.LOG_BACKUP_COUNT
    )

    # Format logs with module names
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not logger.handlers: 
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger