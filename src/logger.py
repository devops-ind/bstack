#!/usr/bin/env python3
"""
Logging Configuration Module
=============================
This module sets up colored logging for the application.
Logs are printed to console and optionally saved to a file.

Key Features:
- Color-coded log levels (Green=INFO, Yellow=WARNING, Red=ERROR, etc.)
- Both console and file logging
- Timestamp for each log message
"""

import logging
import sys
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """
    Custom log formatter that adds colors to console output

    ANSI Color Codes:
    - Cyan (36): DEBUG messages
    - Green (32): INFO messages
    - Yellow (33): WARNING messages
    - Red (31): ERROR messages
    - Magenta (35): CRITICAL messages
    """

    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'  # Reset to default color

    def format(self, record):
        """
        Format log record with color codes

        Args:
            record: LogRecord object from Python logging

        Returns:
            Formatted log message with color
        """
        # Add color codes to level name if color exists
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"

        # Format the message using parent class formatter
        result = super().format(record)
        return result


def setup_logger(log_level=logging.INFO, log_file=None):
    """
    Setup and configure the root logger for the application

    This function:
    1. Creates console handler with colored output
    2. Creates file handler if log_file specified
    3. Configures log format with timestamp

    Args:
        log_level: Logging level (logging.DEBUG, logging.INFO, etc.)
        log_file: Optional path to log file

    Returns:
        Configured logger object
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # --- Setup Console Handler (with colors) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create colored formatter
    console_formatter = ColoredFormatter(
        fmt='[%(asctime)s] %(levelname)-8s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # --- Setup File Handler (if specified) ---
    if log_file:
        # Create parent directories if needed
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(log_path, mode='a')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file

        # Create formatter for file (no colors needed)
        file_formatter = logging.Formatter(
            fmt='[%(asctime)s] %(levelname)-8s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name):
    """
    Get a logger for a specific module

    Usage:
        log = get_logger(__name__)
        log.info("Hello world")

    Args:
        name (str): Logger name (typically __name__)

    Returns:
        Logger object for this module
    """
    return logging.getLogger(name)
