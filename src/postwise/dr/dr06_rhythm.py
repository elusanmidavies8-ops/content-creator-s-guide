"""DR06 — build the weekly rhythm.

Type: PURE. No AI. No clock.

Contract: CreatorInput -> RhythmPlan

Slot count is derived from hours_per_week via a fixed budget table. Days
and dayparts are assigned from fixed tables. Platforms and formats are
rotated through the creator's choices. Pillars cycle magnet -> authority
-> affinity.

Note: DR06 does NOT take Strategy as input. Pillar is a fixed cycle of the
three types; it does not depend on which specific ideas Strategy suggested.
The idea lives on Strategy, and DR07 looks it up by pillar.
"""

from postwise.schemas import (
    CreatorInput,
    DayOfWeek,
    Daypart,
    Pillar,
    Platform,
    RhythmPlan,
    Slot,
)

# (min_hours, max_hours, slot_count)
_BUDGET_TABLE: list[tuple[int, int, int]] = [
    (1, 2, 2),
    (3, 5, 3),
    (6, 10, 4),
    (11, 80, 5),
]

_DAYS_BY_COUNT: dict[int, list[DayOfWeek]] = {
    2: [DayOfWeek.TUE, DayOfWeek.FRI],
    3: [DayOfWeek.MON, DayOfWeek.WED, DayOfWeek.FRI],
    4: [DayOfWeek.MON, DayOfWeek.TUE, DayOfWeek.THU, DayOfWeek.FRI],
    5: [
        DayOfWeek.MON,
        DayOfWeek.TUE,
        DayOfWeek.WED,
        DayOfWeek.THU,
        DayOfWeek.FRI,
    ],
}

_PILLAR_CYCLE: list[Pillar] = [
    Pillar.MAGNET,
    Pillar.AUTHORITY,
    Pillar.AFFINITY,
]

_DAYPART_BY_PLATFORM: dict[Platform, Daypart] = {
    Platform.INSTAGRAM: Daypart.EVENING,
    Platform.TIKTOK: Daypart.EVENING,
    Platform.YOUTUBE: Daypart.AFTERNOON,
    Platform.X: Daypart.MORNING,
    Platform.LINKEDIN: Daypart.MORNING,
    Platform.FACEBOOK: Daypart.AFTERNOON,
    Platform.THREADS: Daypart.EVENING,
    Platform.SUBSTACK: Daypart.MORNING,
    Platform.MEDIUM: Daypart.MORNING,
    Platform.BLOG: Daypart.MORNING,
    Platform.PODCAST: Daypart.MORNING,
}


def run(inp: CreatorInput) -> RhythmPlan:
    count = _slots_for_hours(inp.hours_per_week)
    days = _DAYS_BY_COUNT[count]

    slots: list[Slot] = []
    for i in range(count):
        day = days[i]
        platform = inp.platforms[i % len(inp.platforms)]
        fmt = inp.formats[i % len(inp.formats)]
        pillar = _PILLAR_CYCLE[i % len(_PILLAR_CYCLE)]
        daypart = _DAYPART_BY_PLATFORM[platform]
        slot_id = f"{day.value}-{daypart.value}-{i + 1}"
        slots.append(
            Slot(
                slot_id=slot_id,
                day=day,
                daypart=daypart,
                platform=platform,
                format=fmt,
                pillar=pillar,
            )
        )
    return RhythmPlan(slots=slots)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _slots_for_hours(hours: int) -> int:
    for lo, hi, count in _BUDGET_TABLE:
        if lo <= hours <= hi:
            return count
    raise ValueError(f"hours_per_week={hours} outside budget table")
