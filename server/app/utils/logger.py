# In server/app/utils/logger.py
"""
Logging configuration
Path: backend/app/utils/logger.py
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """Setup logger with console and file handlers."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"
    
    logger = logging.getLogger("crops_tracker")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

default_logger = setup_logger()