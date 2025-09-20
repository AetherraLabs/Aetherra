#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Unicode-Safe Logging Configuration for Aetherra OS.

Provides logging that properly handles Unicode characters and emojis.
"""

# Standard library imports
import logging
import sys
from collections.abc import Mapping
from logging.handlers import RotatingFileHandler
from typing import Any


def ensure_unicode(text: str) -> str:
    try:
        return text.encode("utf-8", errors="replace").decode("utf-8")
    except Exception:  # pragma: no cover
        return text


class UnicodeFormatter(logging.Formatter):
    """Custom formatter that safely handles Unicode characters."""

    def format(self, record: logging.LogRecord) -> str:
        try:
            return super().format(record)
        except UnicodeError:
            # Fallback: replace problematic characters
            record.msg = str(record.msg).encode("ascii", "replace").decode("ascii")
            return super().format(record)


def setup_unicode_logging(level: int = logging.INFO) -> logging.Logger:
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


class SafeLogger:
    """Proxy wrapper providing safe_* methods while delegating all other attributes."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def __getattr__(self, name: str) -> Any:  # delegate normal Logger API
        return getattr(self._logger, name)

    def _safe_log(
        self,
        level: int,
        msg: object,
        *args: object,
        exc_info: Any | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        try:
            self._logger.log(
                level,
                msg,
                *args,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel,
                extra=extra,
            )
        except UnicodeError:
            safe_msg = str(msg).encode("ascii", "replace").decode("ascii")
            self._logger.log(
                level,
                safe_msg,
                *args,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel,
                extra=extra,
            )

    def safe_info(self, msg: object, *args: object, **kwargs: object) -> None:
        extra_obj = kwargs.get("extra")
        extra_map: Mapping[str, object] | None = (
            extra_obj if isinstance(extra_obj, Mapping) else None
        )
        stacklevel_obj = kwargs.get("stacklevel", 1)
        stacklevel_val = stacklevel_obj if isinstance(stacklevel_obj, int) else 1
        self._safe_log(
            logging.INFO,
            msg,
            *args,
            exc_info=kwargs.get("exc_info"),
            stack_info=bool(kwargs.get("stack_info", False)),
            stacklevel=stacklevel_val,
            extra=extra_map,
        )

    def safe_warning(self, msg: object, *args: object, **kwargs: object) -> None:
        extra_obj = kwargs.get("extra")
        extra_map: Mapping[str, object] | None = (
            extra_obj if isinstance(extra_obj, Mapping) else None
        )
        stacklevel_obj = kwargs.get("stacklevel", 1)
        stacklevel_val = stacklevel_obj if isinstance(stacklevel_obj, int) else 1
        self._safe_log(
            logging.WARNING,
            msg,
            *args,
            exc_info=kwargs.get("exc_info"),
            stack_info=bool(kwargs.get("stack_info", False)),
            stacklevel=stacklevel_val,
            extra=extra_map,
        )

    def safe_error(self, msg: object, *args: object, **kwargs: object) -> None:
        extra_obj = kwargs.get("extra")
        extra_map: Mapping[str, object] | None = (
            extra_obj if isinstance(extra_obj, Mapping) else None
        )
        stacklevel_obj = kwargs.get("stacklevel", 1)
        stacklevel_val = stacklevel_obj if isinstance(stacklevel_obj, int) else 1
        self._safe_log(
            logging.ERROR,
            msg,
            *args,
            exc_info=kwargs.get("exc_info"),
            stack_info=bool(kwargs.get("stack_info", False)),
            stacklevel=stacklevel_val,
            extra=extra_map,
        )


def get_safe_logger(name: str) -> SafeLogger:
    """Get a Unicode-safe logger proxy instance with safe_* methods."""
    logger = logging.getLogger(name)
    return SafeLogger(logger)


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
    # Duplicates removed to avoid repeated dictionary keys
}


def safe_emoji_message(message: str) -> str:
    """Convert emojis to safe alternatives for Windows console."""
    if sys.platform == "win32":
        for emoji, safe in SAFE_EMOJIS.items():
            message = message.replace(emoji, safe)
    return message
