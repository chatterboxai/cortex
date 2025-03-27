import logging
import os
import sys


def setup_logging():
    """
    Configure logging for the application.
    
    In DEV environment, DEBUG level logs are shown.
    In other environments, only INFO level and above are shown.
    """
    # Determine environment
    environment = os.environ.get("ENVIRONMENT", "PROD").upper()
    is_dev = environment == "DEV"
    
    # Set log level based on environment
    log_level = logging.DEBUG if is_dev else logging.INFO
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplication
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter with detailed output in dev, more concise in prod
    if is_dev:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific module log levels
    auth_logger = logging.getLogger("app.auth")
    auth_logger.setLevel(log_level)
    
    # Log the current configuration
    root_logger.info(f"Logging configured: environment={environment}, level={logging.getLevelName(log_level)}")
    
    return root_logger
