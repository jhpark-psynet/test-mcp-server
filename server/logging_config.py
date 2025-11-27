"""로깅 설정."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """구조화된 로깅 설정.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path (e.g., "logs/server.log")
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create handlers
    handlers = []

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File handler (if log_file is provided)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # RotatingFileHandler: 10MB per file, keep 5 backup files
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True  # Override any existing configuration
    )

    # Set third-party loggers to WARNING
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
