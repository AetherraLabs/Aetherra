#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Unicode-safe logging helpers (alpha utility)."""


def ensure_unicode(text: str) -> str:
    try:
        return text.encode("utf-8", errors="replace").decode("utf-8")
    except Exception:  # pragma: no cover
        return text


#!/usr/bin/env python3
"""
🌌 Unicode-Safe Logging Configuration for Aetherra OS
====================================================
Provides logging that properly handles Unicode characters and emojis.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler


class UnicodeFormatter(logging.Formatter):
    """Custom formatter that safely handles Unicode characters."""

    def format(self, record):
        try:
            return super().format(record)
        except UnicodeError:
            # Fallback: replace problematic characters
            record.msg = str(record.msg).encode("ascii", "replace").decode("ascii")
            return super().format(record)


def setup_unicode_logging(level=logging.INFO):
    """Set up Unicode-safe logging for Aetherra OS."""

    # Clear any existing handlers
    logging.getLogger().handlers.clear()

    # Create formatters
    unicode_formatter = UnicodeFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(unicode_formatter)
    console_handler.setLevel(level)

    # File handler with UTF-8 encoding
    file_handler = RotatingFileHandler(
        "aetherra_os.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(unicode_formatter)
    file_handler.setLevel(level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return root_logger


def get_safe_logger(name):
    """Get a Unicode-safe logger instance."""
    logger = logging.getLogger(name)

    # Add a safe logging method that handles Unicode errors
    def safe_log(level, msg, *args, **kwargs):
        try:
            logger.log(level, msg, *args, **kwargs)
        except UnicodeError:
            # Fallback: convert to safe ASCII
            safe_msg = str(msg).encode("ascii", "replace").decode("ascii")
            logger.log(level, safe_msg, *args, **kwargs)

    logger.safe_info = lambda msg, *args, **kwargs: safe_log(
        logging.INFO, msg, *args, **kwargs
    )
    logger.safe_error = lambda msg, *args, **kwargs: safe_log(
        logging.ERROR, msg, *args, **kwargs
    )
    logger.safe_warning = lambda msg, *args, **kwargs: safe_log(
        logging.WARNING, msg, *args, **kwargs
    )

    return logger


# Safe emoji alternatives for Windows console
SAFE_EMOJIS = {
    "🌌": "[COSMOS]",
    "🔥": "[FIRE]",
    "🌐": "[GLOBE]",
    "🧠": "[BRAIN]",
    "🔌": "[PLUG]",
    "⚡": "[BOLT]",
    "🎉": "[PARTY]",
    "🚀": "[ROCKET]",
    "💾": "[DISK]",
    "📅": "[CALENDAR]",
    "🔄": "[REFRESH]",
    "🛑": "[STOP]",
    "📊": "[CHART]",
    "❌": "[X]",
    "✅": "[CHECK]",
    "💡": "[BULB]",
    "🔍": "[SEARCH]",
    "📁": "[FOLDER]",
    "🌟": "[STAR]",
    "🎯": "[TARGET]",
    "🏗️": "[CONSTRUCTION]",
    "🔧": "[WRENCH]",
    "📝": "[MEMO]",
    "🔐": "[LOCK]",
    "🌊": "[WAVE]",
    "🎨": "[PALETTE]",
    "🔬": "[MICROSCOPE]",
    "🎪": "[CIRCUS]",
    "🏆": "[TROPHY]",
    "💎": "[DIAMOND]",
    "🚨": "[ALARM]",
    "🎭": "[THEATER]",
    "🌈": "[RAINBOW]",
    "🎼": "[MUSIC]",
    "🔮": "[CRYSTAL]",
    "🎲": "[DICE]",
    "🎳": "[BOWLING]",
    "🌸": "[BLOSSOM]",
    "🦋": "[BUTTERFLY]",
    "🌺": "[HIBISCUS]",
    "🌻": "[SUNFLOWER]",
    "🍀": "[CLOVER]",
    "🌙": "[MOON]",
    "⭐": "[STAR]",
    "☀️": "[SUN]",
    "🌡️": "[THERMOMETER]",
    "🎪": "[TENT]",
    "🎨": "[ART]",
}


def safe_emoji_message(message):
    """Convert emojis to safe alternatives for Windows console."""
    if sys.platform == "win32":
        for emoji, safe in SAFE_EMOJIS.items():
            message = message.replace(emoji, safe)
    return message
