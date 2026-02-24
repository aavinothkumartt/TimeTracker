"""Configuration settings for TimeTracker app."""
import os
from pathlib import Path

# Application info
APP_NAME = "TimeTracker"
APP_VERSION = "1.0.0"

# Paths
HOME_DIR = Path.home()
APP_DATA_DIR = HOME_DIR / ".timetracker"
DATABASE_PATH = APP_DATA_DIR / "timetracker.db"

# Create data directory if it doesn't exist
APP_DATA_DIR.mkdir(exist_ok=True)

# UI Configuration
UPDATE_INTERVAL = 1  # seconds - how often to update timer display
ICON_IDLE = "⏱"  # Icon when no session is running
ICON_ACTIVE = "▶"  # Icon when session is active

# Date/Time formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"
