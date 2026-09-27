"""Structured logging configuration."""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure and return the root application logger."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(numeric_level)

    root_logger = logging.getLogger("app")
    root_logger.setLevel(numeric_level)

    # Prevent adding multiple handlers during re-initialization
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers.clear()
        root_logger.addHandler(handler)

    root_logger.propagate = False
    return root_logger
