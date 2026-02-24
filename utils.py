"""Utility functions for time formatting and parsing."""
import re
from datetime import datetime
import config


def format_duration(seconds):
    """
    Convert seconds to human-readable format.

    Args:
        seconds (int): Duration in seconds

    Returns:
        str: Formatted duration (e.g., "2h 30m" or "45m" or "30s")
    """
    if seconds < 0:
        return "0s"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"
    elif minutes > 0:
        if secs > 0:
            return f"{minutes}m {secs}s"
        return f"{minutes}m"
    else:
        return f"{secs}s"


def format_duration_detailed(seconds):
    """
    Convert seconds to detailed time format with leading zeros.

    Args:
        seconds (int): Duration in seconds

    Returns:
        str: Formatted duration (e.g., "02:30:15" for 2h 30m 15s)
    """
    if seconds < 0:
        return "00:00:00"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_duration(duration_str):
    """
    Parse duration string to seconds.

    Supports formats like:
    - "2h 30m"
    - "2h30m"
    - "150m"
    - "90m"
    - "2.5h"
    - "1.5"  (interpreted as hours)

    Args:
        duration_str (str): Duration string

    Returns:
        int: Duration in seconds, or None if parsing fails
    """
    if not duration_str or not duration_str.strip():
        return None

    duration_str = duration_str.strip().lower()
    total_seconds = 0

    try:
        # Try to match hours and minutes patterns
        # Pattern: "2h 30m" or "2h30m" or "2h" or "30m"
        hour_pattern = r'(\d+(?:\.\d+)?)\s*h'
        minute_pattern = r'(\d+(?:\.\d+)?)\s*m'

        hour_match = re.search(hour_pattern, duration_str)
        minute_match = re.search(minute_pattern, duration_str)

        if hour_match:
            hours = float(hour_match.group(1))
            total_seconds += int(hours * 3600)

        if minute_match:
            minutes = float(minute_match.group(1))
            total_seconds += int(minutes * 60)

        # If we found at least one pattern, return the result
        if hour_match or minute_match:
            return total_seconds

        # Try to parse as just a number (assume hours)
        try:
            value = float(duration_str)
            return int(value * 3600)
        except ValueError:
            pass

        return None

    except Exception:
        return None


def get_today_date():
    """
    Get today's date in standard format.

    Returns:
        str: Today's date (YYYY-MM-DD)
    """
    return datetime.now().strftime(config.DATE_FORMAT)


def get_current_datetime():
    """
    Get current datetime in standard format.

    Returns:
        str: Current datetime (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime(config.DATETIME_FORMAT)


def parse_datetime(datetime_str):
    """
    Parse datetime string to datetime object.

    Args:
        datetime_str (str): Datetime string in DATETIME_FORMAT

    Returns:
        datetime: Parsed datetime object, or None if parsing fails
    """
    try:
        return datetime.strptime(datetime_str, config.DATETIME_FORMAT)
    except Exception:
        return None


def calculate_duration_seconds(start_time_str, end_time_str):
    """
    Calculate duration in seconds between two datetime strings.

    Args:
        start_time_str (str): Start datetime string
        end_time_str (str): End datetime string

    Returns:
        int: Duration in seconds, or None if parsing fails
    """
    start = parse_datetime(start_time_str)
    end = parse_datetime(end_time_str)

    if not start or not end:
        return None

    duration = end - start
    return int(duration.total_seconds())
