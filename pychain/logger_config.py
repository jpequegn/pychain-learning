"""
Centralized logging configuration for PyChain.

This module provides a unified logging setup for all PyChain components,
supporting both console and file output with configurable log levels.
"""

import logging
import sys
from pathlib import Path


def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up logger with console and optional file output.

    Args:
        name (str): Logger name (e.g., 'pychain', 'pychain.block')
        log_file (str, optional): Log file path for persistent logging
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logger('pychain', log_file='blockchain.log', level=logging.DEBUG)
        >>> logger.info('Blockchain initialized')
        >>> logger.debug('Detailed debug information')
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    # Format for log messages with timestamp, logger name, level, and message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler - outputs to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional) - outputs to log file
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name):
    """
    Get an existing logger or create a new one with default settings.

    Args:
        name (str): Logger name

    Returns:
        logging.Logger: Logger instance

    Example:
        >>> logger = get_logger('pychain.blockchain')
        >>> logger.info('Operation completed')
    """
    logger = logging.getLogger(name)

    # If logger not configured, set it up with default settings
    if not logger.handlers:
        return setup_logger(name)

    return logger


def set_log_level(logger_name, level):
    """
    Change the log level for an existing logger.

    Args:
        logger_name (str): Name of the logger to modify
        level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> set_log_level('pychain', logging.DEBUG)
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Update all handlers
    for handler in logger.handlers:
        handler.setLevel(level)


# Create default logger for the pychain package
default_logger = setup_logger('pychain')
