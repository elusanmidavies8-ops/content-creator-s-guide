"""DR06 — pure rhythm. Deterministic from hours + platforms + formats."""

from postwise.dr import dr06_rhythm
from postwise.schemas import (
    CreatorInput,
    DayOfWeek,
    Format,
    Pillar,
    Platform,
    RhythmPlan,
)


def _inp(hours: int, platforms=None, formats=None) -> CreatorInput:
    return CreatorInput(
        makes_and_audience="comedy for Gen Z",
        goal_90d="grow",
        hours_per_week=hours,
        audience_locations=["Nigeria"],
        platforms=platforms or [Platform.INSTAGRAM],
        formats=formats or [Format.SHORT_VIDEO],
    )


def test_returns_rhythm_plan():
    plan = dr06_rhythm.run(_inp(6))
    assert isinstance(plan, RhythmPlan)


def test_two_hours_produces_two_slots():
    plan = dr06_rhythm.run(_inp(2))
    assert len(plan.slots) == 2


def test_three_hours_produces_three_slots():
    plan = dr06_rhythm.run(_inp(4))
    assert len(plan.slots) == 3


def test_six_hours_produces_four_slots():
    plan = dr06_rhythm.run(_inp(6))
    assert len(plan.slots) == 4


def test_high_hours_produces_five_slots():
    plan = dr06_rhythm.run(_inp(20))
    assert len(plan.slots) == 5


def test_slots_use_only_chosen_platforms():
    plan = dr06_rhythm.run(_inp(6, platforms=[Platform.INSTAGRAM, Platform.TIKTOK]))
    for slot in plan.slots:
        assert slot.platform in (Platform.INSTAGRAM, Platform.TIKTOK)


def test_slots_use_only_chosen_formats():
    plan = dr06_rhythm.run(_inp(6, formats=[Format.SHORT_VIDEO, Format.TEXT]))
    for slot in plan.slots:
        assert slot.format in (Format.SHORT_VIDEO, Format.TEXT)


def test_pillars_cycle_magnet_authority_affinity():
    plan = dr06_rhythm.run(_inp(6))
    expected = [
        Pillar.MAGNET,
        Pillar.AUTHORITY,
        Pillar.AFFINITY,
        Pillar.MAGNET,
    ]
    assert [s.pillar for s in plan.slots] == expected


def test_slot_ids_are_unique():
    plan = dr06_rhythm.run(_inp(6, platforms=[Platform.INSTAGRAM, Platform.TIKTOK]))
    ids = [s.slot_id for s in plan.slots]
    assert len(ids) == len(set(ids))


def test_days_are_unique_per_slot():
    plan = dr06_rhythm.run(_inp(6))
    days = [s.day for s in plan.slots]
    assert len(days) == len(set(days))


def test_all_days_are_weekdays():
    plan = dr06_rhythm.run(_inp(6))
    weekend = {DayOfWeek.SAT, DayOfWeek.SUN}
    for slot in plan.slots:
        assert slot.day not in weekend
