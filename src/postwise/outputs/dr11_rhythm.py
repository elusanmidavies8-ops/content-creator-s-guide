"""DR11 — weekly rhythm.

Type: PURE. No AI.

Contract: RhythmPlan -> RhythmPlan

Pass-through today: DR06 already produces exactly what the creator sees.
The module exists so DR11 is a named boundary; enrichment (calendar view,
hour estimates per slot) would land here.
"""

from postwise.schemas import RhythmPlan


def build(rhythm: RhythmPlan) -> RhythmPlan:
    return rhythm
