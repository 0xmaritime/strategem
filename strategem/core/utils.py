"""Strategem Core - Utility Functions (Mechanical Only)"""

import logging
from pathlib import Path
from typing import Any
from .primitives import get_timestamp


# Configure logging (mechanical only)
def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Setup logging configuration (mechanical only).

    Args:
        level: Logging level
        log_file: Optional path to log file

    Returns:
        Configured logger
    """
    logger = logging.getLogger("strategem")
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def truncate_string(s: str, max_length: int = 100) -> str:
    """
    Truncate string with ellipsis if too long (mechanical only).

    Args:
        s: String to truncate
        max_length: Maximum length

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - 3] + "..."


def safe_get_nested(data: dict, *keys, default: Any = None) -> Any:
    """
    Safely get nested dictionary value (mechanical only).

    Args:
        data: Dictionary to search
        *keys: Nested keys to traverse
        default: Default value if not found

    Returns:
        Value at nested keys or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def merge_dicts(*dicts: dict) -> dict:
    """
    Merge multiple dictionaries (mechanical only).

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def chunks(lst: list, chunk_size: int) -> list[list]:
    """
    Split list into chunks (mechanical only).

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format (mechanical only).

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_timestamp(timestamp) -> str:
    """
    Format timestamp for display (mechanical only).

    Args:
        timestamp: datetime object

    Returns:
        Formatted timestamp string
    """
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")
