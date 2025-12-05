# backend/app/utils/logging_setup.py

import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from app.config import get_config # <-- Needed to fetch logging settings

def setup_logging(app):
    """
    Configures application-wide logging based on settings in config.py
    """
    config = app.config
    
    # Skip setup if running tests
    if config.get('TESTING'):
        return

    log_level = config.get('LOG_LEVEL', 'INFO')
    log_file_path = config.get('LOG_FILE')
    log_format = config.get('LOG_FORMAT')
    max_bytes = config.get('LOG_MAX_BYTES')
    backup_count = config.get('LOG_BACKUP_COUNT')
    
    # 1. Ensure log directory exists
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. Configure the root logger
    formatter = logging.Formatter(log_format)
    
    # Set up file handler (for persistent logs)
    file_handler = RotatingFileHandler(
        log_file_path, 
        maxBytes=max_bytes, 
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    
    # Set up console handler (for terminal output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 3. Apply handlers and level to the Flask app's logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Suppress verbose loggers from external libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    app.logger.info("Application logging successfully configured.")

# Security Logger Wrapper
class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
    
    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
        
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
        
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def log_alert(self, alert):
        """Log a security alert event"""
        self.logger.info(
            f"SECURITY ALERT: [{alert.severity.upper()}] {alert.title} "
            f"(Source: {alert.source}, IP: {alert.ip_address})"
        )

security_logger = SecurityLogger()