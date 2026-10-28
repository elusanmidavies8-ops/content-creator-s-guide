"""DR01 — warnings for skipped optional fields. Pure, deterministic."""

from typing import Any

from postwise.dr import dr01_check
from postwise.schemas import CreatorInput, Format, Platform


def _make(**overrides: Any) -> CreatorInput:
    base: dict[str, Any] = dict(
        makes_and_audience="comedy skits for Nigerian Gen Z",
        goal_90d="grow to 5000 followers",
        goal_number=5000,
        hours_per_week=6,
        audience_locations=["Nigeria"],
        platforms=[Platform.INSTAGRAM],
        formats=[Format.SHORT_VIDEO],
    )
    base.update(overrides)
    return CreatorInput(**base)


def test_no_warnings_when_optional_fields_filled() -> None:
    inp = _make(samples=["hello world"], dm_questions=["how do you do this?"])
    out = dr01_check.run(inp)
    assert out.warnings == []
    assert out.input is inp


def test_warns_when_samples_missing() -> None:
    out = dr01_check.run(_make(dm_questions=["q1", "q2"]))
    assert any("DR03" in w for w in out.warnings)


def test_warns_when_dm_questions_missing() -> None:
    out = dr01_check.run(_make(samples=["sample"]))
    assert any("DR04" in w for w in out.warnings)


def test_two_warnings_when_both_missing() -> None:
    out = dr01_check.run(_make())
    assert len(out.warnings) == 2


def test_never_rejects_valid_input() -> None:
    inp = _make()
    out = dr01_check.run(inp)  # must not raise
    assert out.input.hours_per_week == 6
