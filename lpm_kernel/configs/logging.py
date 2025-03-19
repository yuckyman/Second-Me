import os
import sys

# Get project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DEFAULT_LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# Ensure log directory exists
os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)

# Clear log file
log_file_path = os.path.join(DEFAULT_LOG_DIR, "app.log")
with open(log_file_path, "w") as f:
    pass  # Clear log file content


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": os.path.join(DEFAULT_LOG_DIR, "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "root": {  # root logger configuration
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}
