# common/logging.py
import logging
import logging.config
import os
import sys
from lpm_kernel.configs.logging import LOGGING_CONFIG, DEFAULT_LOG_DIR


def setup_logging():
    try:
        # Ensure log directory exists
        os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
        # Ensure directory permissions are correct
        os.chmod(DEFAULT_LOG_DIR, 0o755)

        print(f"Log directory: {DEFAULT_LOG_DIR}", file=sys.stderr)
        print(
            f"Log file: {LOGGING_CONFIG['handlers']['file']['filename']}",
            file=sys.stderr,
        )

    except Exception as e:
        print(f"Error creating log directory: {e}", file=sys.stderr)
        # If unable to create directory, use standard output
        LOGGING_CONFIG["handlers"]["file"] = LOGGING_CONFIG["handlers"]["console"]

    try:
        # Configure logging
        logging.config.dictConfig(LOGGING_CONFIG)
        root_logger = logging.getLogger()
        root_logger.info("Logging system initialized successfully")
        print(f"Log level: {root_logger.getEffectiveLevel()}", file=sys.stderr)
        print(
            f"Log handlers: {[h.__class__.__name__ for h in root_logger.handlers]}",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"Error configuring logging: {e}", file=sys.stderr)
        # If configuration fails, use basic configuration
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Get module logger
    logger = logging.getLogger(__name__)
    logger.info("Logging module initialization complete")
    return logger


# Initialize global logger
logger = setup_logging()

# Test logging
logger.debug("DEBUG: Logging module loaded")
logger.info("INFO: Logging module loaded")
logger.warning("WARNING: Logging module loaded")
logger.error("ERROR: Logging module loaded")
