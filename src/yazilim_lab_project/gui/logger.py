"""Logging utility for GUI actions and engine execution."""

import logging
import sys
from pathlib import Path

# Create logs directory under workspace root if possible, or relative to project
LOG_DIR = Path.cwd() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "gui_activity.log"

logger = logging.getLogger("yazilim_lab_gui")
logger.setLevel(logging.DEBUG)

# File handler with UTF-8
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_fmt = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(file_fmt)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_fmt = logging.Formatter(
    "[%(asctime)s] [%(levelname)s]: %(message)s",
    datefmt="%H:%M:%S",
)
console_handler.setFormatter(console_fmt)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_gui_action(action_name: str, **kwargs) -> None:
    """Log an interaction from the user in GUI (button clicks, selections, etc.)."""
    details = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"UI ACTION -> {action_name} | {details}" if details else f"UI ACTION -> {action_name}")


def log_command_execution(cmd: object, result: object | None = None, error: Exception | None = None) -> None:
    """Log engine execution of a command and its result or error."""
    cmd_str = (
        cmd.model_dump_json(by_alias=True)
        if hasattr(cmd, "model_dump_json")
        else str(cmd)
    )
    if error:
        logger.error(f"ENGINE ERROR executing command: {cmd_str}\nException: {error}", exc_info=True)
    elif result:
        res_str = (
            result.model_dump_json(by_alias=True, exclude_none=True)
            if hasattr(result, "model_dump_json")
            else str(result)
        )
        logger.info(f"COMMAND EXECUTED -> {cmd_str} --> RESULT: {res_str}")
