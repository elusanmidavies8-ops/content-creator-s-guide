"""DR11 — view preserves the DR06 rhythm plan."""

from postwise.outputs import dr11_rhythm
from postwise.schemas import (
    DayOfWeek,
    Daypart,
    Format,
    Pillar,
    Platform,
    RhythmPlan,
    Slot,
)


def _plan() -> RhythmPlan:
    return RhythmPlan(
        slots=[
            Slot(
                slot_id="tue-evening-1",
                day=DayOfWeek.TUE,
                daypart=Daypart.EVENING,
                platform=Platform.INSTAGRAM,
                format=Format.SHORT_VIDEO,
                pillar=Pillar.MAGNET,
            ),
            Slot(
                slot_id="fri-evening-2",
                day=DayOfWeek.FRI,
                daypart=Daypart.EVENING,
                platform=Platform.INSTAGRAM,
                format=Format.SHORT_VIDEO,
                pillar=Pillar.AUTHORITY,
            ),
        ]
    )


def test_returns_rhythm_plan():
    result = dr11_rhythm.build(_plan())
    assert isinstance(result, RhythmPlan)


def test_slots_preserved():
    plan = _plan()
    result = dr11_rhythm.build(plan)
    assert result.slots == plan.slots
