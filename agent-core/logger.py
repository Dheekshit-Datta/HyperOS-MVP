"""
HyperOS Structured Logging
Rotating file handler, colored console output, correlation IDs
"""

import os
import sys
import logging
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from contextvars import ContextVar
from datetime import datetime

# Context variable for request correlation ID
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')


# =============================================================================
# COLORED FORMATTER
# =============================================================================

class ColoredFormatter(logging.Formatter):
    """
    Formatter that adds ANSI colors to log levels for console output.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
    
    def format(self, record: logging.LogRecord) -> str:
        # Get color for this level
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Add correlation ID if available
        corr_id = correlation_id.get()
        if corr_id:
            record.correlation_id = corr_id[:8]
        else:
            record.correlation_id = '--------'
        
        # Format the message
        formatted = super().format(record)
        
        # Apply color to level name in the message
        formatted = formatted.replace(
            record.levelname,
            f"{color}{self.BOLD}{record.levelname}{self.RESET}"
        )
        
        return formatted


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs structured JSON logs for production.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        import json
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id.get() or None,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'stack_info', 'exc_info', 'exc_text', 'message', 'correlation_id'
            ]:
                log_entry[key] = value
        
        return json.dumps(log_entry)


# =============================================================================
# LOGGER CONFIGURATION
# =============================================================================

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = "logs/hyperos.log",
    max_size_mb: int = 10,
    backup_count: int = 5,
    json_format: bool = False
) -> logging.Logger:
    """
    Configure the HyperOS logger with console and file handlers.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file, or None to disable file logging
        max_size_mb: Max log file size before rotation
        backup_count: Number of backup files to keep
        json_format: Use JSON format for file logs
        
    Returns:
        Configured root logger
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console format
    console_format = (
        "%(asctime)s │ %(levelname)-8s │ [%(correlation_id)s] │ "
        "%(name)-20s │ %(message)s"
    )
    console_datefmt = "%H:%M:%S"
    
    # File format
    file_format = (
        "%(asctime)s | %(levelname)-8s | %(correlation_id)s | "
        "%(name)s | %(funcName)s:%(lineno)d | %(message)s"
    )
    file_datefmt = "%Y-%m-%d %H:%M:%S"
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(console_format, console_datefmt)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        if json_format:
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(file_format, file_datefmt))
        
        root_logger.addHandler(file_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"HyperOS.{name}")


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """
    Set the correlation ID for the current context.
    
    Args:
        corr_id: Correlation ID, or None to generate one
        
    Returns:
        The correlation ID set
    """
    if corr_id is None:
        corr_id = str(uuid.uuid4())
    correlation_id.set(corr_id)
    return corr_id


def get_correlation_id() -> str:
    """Get the current correlation ID"""
    return correlation_id.get()


# =============================================================================
# LOGGING CONTEXT MANAGER
# =============================================================================

class LogContext:
    """
    Context manager for adding correlation ID to logs.
    
    Usage:
        with LogContext() as ctx:
            logger.info("This log has correlation ID")
            print(f"Request ID: {ctx.correlation_id}")
    """
    
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self._token = None
    
    def __enter__(self) -> 'LogContext':
        self._token = set_correlation_id(self.correlation_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        correlation_id.set('')


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def log_task_start(task: str, task_id: str) -> None:
    """Log task start with context"""
    logger = get_logger("Agent")
    set_correlation_id(task_id)
    logger.info(f"Task started: {task[:100]}")


def log_task_end(task_id: str, status: str, steps: int) -> None:
    """Log task completion"""
    logger = get_logger("Agent")
    logger.info(f"Task completed: status={status}, steps={steps}")


def log_action(action: str, params: dict, result: str) -> None:
    """Log an action execution"""
    logger = get_logger("Action")
    logger.debug(f"Execute: {action}({params}) -> {result}")


def log_security_event(event_type: str, details: str, severity: str = "WARNING") -> None:
    """Log a security-related event"""
    logger = get_logger("Security")
    log_fn = getattr(logger, severity.lower(), logger.warning)
    log_fn(f"[{event_type}] {details}")


# Initialize default logging
if not logging.getLogger().handlers:
    setup_logging()
