"""
Logging utilities for Lyrixa
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Create logger for Lyrixa
logger = logging.getLogger("Lyrixa")


def log(message: str, level: str = "INFO"):
    """
    Simple logging function with emoji and timestamp

    Args:
        message: The message to log
        level: Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    """
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Add emoji based on level
    emoji_map = {
        "DEBUG": "🔍",
        "INFO": "ℹ️",
        "WARNING": "[WARN]",
        "ERROR": "❌",
        "CRITICAL": "🚨",
    }

    emoji = emoji_map.get(level.upper(), "📝")
    formatted_message = f"{emoji} [{timestamp}] {message}"

    # Log using appropriate level
    if level.upper() == "DEBUG":
        logger.debug(formatted_message)
    elif level.upper() == "WARNING":
        logger.warning(formatted_message)
    elif level.upper() == "ERROR":
        logger.error(formatted_message)
    elif level.upper() == "CRITICAL":
        logger.critical(formatted_message)
    else:
        logger.info(formatted_message)

    # Also print to console for immediate feedback
    print(formatted_message)


def setup_file_logging(log_dir: str | None = None):
    """Setup file logging in addition to console logging"""
    if log_dir is None:
        log_path = Path(__file__).parent.parent / "logs"
    else:
        log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Create file handler
    log_file = log_path / f"lyrixa_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    log(f"File logging enabled: {log_file}")


def log_system_info():
    """Log system information for debugging"""
    import platform
    import sys

    log("System Information:")
    log(f"  Platform: {platform.platform()}")
    log(f"  Python: {sys.version}")
    log(f"  Architecture: {platform.machine()}")


def log_startup_banner():
    """Log the Lyrixa startup banner"""
    banner = """
🧬 ================================ 🧬
🚀     Lyrixa AI Assistant       🚀
[DISC]   Modular Agent Architecture   [DISC]
🧬 ================================ 🧬
"""
    print(banner)
    log("Lyrixa AI Assistant starting up...")


def log_agent_activity(agent_name: str, activity: str, details: str = ""):
    """Log agent-specific activity"""
    message = f"[{agent_name}] {activity}"
    if details:
        message += f" - {details}"
    log(message, "DEBUG")


def log_error_with_traceback(message: str, exception: Exception):
    """Log error with full traceback"""
    import traceback

    log(f"ERROR: {message}", "ERROR")
    log(f"Exception: {str(exception)}", "ERROR")
    log(f"Traceback:\n{traceback.format_exc()}", "ERROR")
