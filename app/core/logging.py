"""
Central logging configuration for the RAG system.
"""

import logging
import sys
from typing import Optional
from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Setup centralized logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string
        use_colors: Whether to use colored output

    Returns:
        Configured logger instance
    """
    # Get log level from config or parameter
    log_level = level or settings.LOG_LEVEL

    # Default format string
    if format_string is None:
        format_string = "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s"

    # Create formatter
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(format_string)
    else:
        formatter = logging.Formatter(format_string)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    configure_loggers()

    return root_logger


def configure_loggers():
    """Configure specific loggers with appropriate levels."""
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)

    # Set our app loggers to DEBUG for detailed logging
    app_loggers = [
        "app",
        "app.core",
        "app.application",
        "app.infrastructure",
        "app.presentation",
    ]

    for logger_name in app_loggers:
        logging.getLogger(logger_name).setLevel(logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Log function call with parameters.

    Args:
        logger: Logger instance
        func_name: Function name
        **kwargs: Function parameters
    """
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"Calling {func_name}({params})")


def log_function_result(logger: logging.Logger, func_name: str, result: any):
    """
    Log function result.

    Args:
        logger: Logger instance
        func_name: Function name
        result: Function result
    """
    logger.debug(f"{func_name} returned: {type(result).__name__}")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Log error with context.

    Args:
        logger: Logger instance
        error: Exception instance
        context: Additional context
    """
    context_str = f" in {context}" if context else ""
    logger.error(f"Error{context_str}: {type(error).__name__}: {str(error)}")


# Initialize logging on import
setup_logging()
