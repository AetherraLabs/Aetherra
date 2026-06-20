"""Runtime UI query parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .observatory import ObservatoryMode


@dataclass(frozen=True, slots=True)
class ParsedLimit:
    """Bounded limit query result."""

    ok: bool
    value: int
    error: str | None = None


def parse_observatory_mode(value: str | None) -> ObservatoryMode | None:
    """Parse a Runtime UI mode value."""

    raw_mode = (value or ObservatoryMode.OVERVIEW.value).strip().lower()
    try:
        return ObservatoryMode(raw_mode)
    except ValueError:
        return None


def bounded_user_name(value: str | None) -> str | None:
    """Normalize and bound an optional display name."""

    if value is None:
        return None
    normalized = " ".join(value.strip().split())
    if not normalized:
        return None
    return normalized[:64]


def bounded_filter_value(value: str | None) -> str | None:
    """Normalize and bound an optional activity filter."""

    if value is None:
        return None
    normalized = value.strip().lower().replace("-", "_")
    if not normalized:
        return None
    return normalized[:64]


def parse_limit(value: str | None, *, default: int) -> ParsedLimit:
    """Parse a bounded activity limit."""

    try:
        limit = int(value or str(default))
    except ValueError:
        return ParsedLimit(ok=False, value=default, error="limit must be an integer")
    return ParsedLimit(ok=True, value=max(1, min(limit, 100)))


def allowed_observatory_modes() -> list[str]:
    """Return supported Runtime UI mode values."""

    return [mode.value for mode in ObservatoryMode]
