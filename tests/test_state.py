"""State layer tests. Sessions isolated by fixture reset."""

import pytest

from postwise import state


@pytest.fixture(autouse=True)
def _clean_sessions() -> None:
    yield
    state.reset("s1")
    state.reset("s2")


def test_mark_made_records_slot() -> None:
    state.mark_made("s1", "tue-evening-1")
    assert state.is_made("s1", "tue-evening-1")


def test_duplicate_mark_is_idempotent() -> None:
    state.mark_made("s1", "tue-evening-1")
    state.mark_made("s1", "tue-evening-1")
    assert len(state.get_made("s1")) == 1


def test_sessions_are_isolated() -> None:
    state.mark_made("s1", "a")
    state.mark_made("s2", "b")
    assert state.get_made("s1") == ["a"]
    assert state.get_made("s2") == ["b"]


def test_get_progress_reports_counts() -> None:
    state.mark_made("s1", "a")
    state.mark_made("s1", "b")
    progress = state.get_progress("s1", total=4)
    assert progress == {"made": 2, "total": 4, "ratio": 0.5}


def test_get_progress_handles_zero_total() -> None:
    progress = state.get_progress("s1", total=0)
    assert progress["ratio"] == 0.0
    assert progress["made"] == 0


def test_get_made_on_unknown_session_is_empty() -> None:
    assert state.get_made("never-seen") == []


def test_reset_clears_session() -> None:
    state.mark_made("s1", "a")
    state.reset("s1")
    assert state.get_made("s1") == []
