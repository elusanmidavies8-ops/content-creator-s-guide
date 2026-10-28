"""Completion tracking for Postwise.

In-memory store keyed by session_id. No DB, no files, no persistence across
restarts — v1 decision. If this ever needs to survive a restart, swap the
implementation for a JsonFileStore with the same three public functions.

The public API is exactly four functions: mark_made, is_made, get_made,
get_progress (plus reset for tests and a future "start over" button).
Nothing else in the codebase knows how it's stored.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TypedDict


class _Session(TypedDict):
    made: list[str]
    started_at: str


_SESSIONS: dict[str, _Session] = {}


def mark_made(session_id: str, slot_id: str) -> None:
    """Record that the creator marked a slot as made. Idempotent."""
    session = _SESSIONS.setdefault(
        session_id,
        _Session(made=[], started_at=_now()),
    )
    if slot_id not in session["made"]:
        session["made"].append(slot_id)


def is_made(session_id: str, slot_id: str) -> bool:
    """True if this slot was marked made in this session."""
    return slot_id in get_made(session_id)


def get_made(session_id: str) -> list[str]:
    """Return made slot IDs in the order they were marked."""
    session = _SESSIONS.get(session_id)
    if session is None:
        return []
    return list(session["made"])


def get_progress(session_id: str, total: int) -> dict[str, int | float]:
    """Returns {'made': N, 'total': T, 'ratio': N/T or 0.0}."""
    made = len(get_made(session_id))
    ratio = (made / total) if total else 0.0
    return {"made": made, "total": total, "ratio": ratio}


def reset(session_id: str) -> None:
    """Clear a session. Used in tests and by a future 'start over' button."""
    _SESSIONS.pop(session_id, None)


def _now() -> str:
    return datetime.now(UTC).isoformat()
