"""
Logging utility for the Job Application MCP Server.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "job-mcp", level: str = "INFO") -> logging.Logger:
    """Create a configured logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.handlers:
        return logger

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s │ %(levelname)-7s │ %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(console)

    # File handler
    log_dir = Path(__file__).parent.parent.parent / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"mcp_{datetime.now():%Y%m%d}.log"

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s │ %(name)s │ %(levelname)-7s │ %(funcName)s │ %(message)s"
    ))
    logger.addHandler(fh)

    return logger


log = setup_logger()
