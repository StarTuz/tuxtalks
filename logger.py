"""
TuxTalks Logging Module

Provides centralized logging with file and console output.
Log levels: ALL, DEBUG, INFO, WARNING, ERROR
"""

import logging
import sys
from pathlib import Path

# Custom ALL level (logs absolutely everything)
logging.ALL = 5
logging.addLevelName(logging.ALL, "ALL")

def setup_logger(name="tuxtalks", log_level="INFO"):
    """
    Setup rotating file logger with console output.
    
    Args:
        name: Logger name
        log_level: String level (ALL, DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_dir = Path.home() / ".local/share/tuxtalks/logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "tuxtalks.log"
    
    # Wipe old log on startup (rotation)
    if log_file.exists():
        log_file.unlink()
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Map string levels to logging constants
    level_map = {
        "ALL": logging.ALL,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler - always logs ALL
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.ALL if hasattr(logging, 'ALL') else logging.DEBUG)
    
    # Console handler - respects log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format with timestamps
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup with warning for ALL level
    if log_level.upper() == "ALL":
        logger.warning("⚠️ Logging level set to ALL - log file may grow large!")
    
    logger.info(f"Logger initialized: level={log_level}, file={log_file}")
    
    return logger

def get_logger(name="tuxtalks"):
    """Get existing logger instance."""
    return logging.getLogger(name)
