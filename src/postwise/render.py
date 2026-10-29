"""Render layer. PipelineResult -> UI dict.

This is the CONTRACT between backend and any UI (Gradio, FastAPI, mobile,
whatever your partner builds). Whoever renders the page consumes exactly
this shape. If the shape changes, the UI breaks — that's the point.

Design:
  - hero     the one brief to look at now (first un-made, else last)
  - queue    the rest, locked, in order
  - plan     everything else, collapsed behind a disclosure

The card carries platform/format/day/daypart/pillar from the matching
rhythm slot, so the UI doesn't need to join anything itself.
"""

from __future__ import annotations

from postwise import state
from postwise.schemas import PipelineResult, ScoredBrief, Slot


def build_view(result: PipelineResult, session_id: str) -> dict[str, object]:
    """Produce the view dict the UI renders. Pure read — never mutates."""
    made = set(state.get_made(session_id))
    progress = state.get_progress(session_id, total=len(result.briefs))
    slot_lookup = {s.slot_id: s for s in result.rhythm.slots}

    if not result.briefs:
        return {
            "session_id": session_id,
            "lane": result.direction.lane,
            "hero": None,
            "queue": [],
            "progress": progress,
            "plan": _plan_summary(result),
        }

    hero_idx = _hero_index(result.briefs, made)
    hero = _brief_to_card(
        result.briefs[hero_idx],
        made,
        slot_lookup,
        is_hero=True,
    )
    queue = [_brief_to_card(b, made, slot_lookup, is_hero=False, locked=True) for i, b in enumerate(result.briefs) if i != hero_idx]

    return {
        "session_id": session_id,
        "lane": result.direction.lane,
        "hero": hero,
        "queue": queue,
        "progress": progress,
        "plan": _plan_summary(result),
    }


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _hero_index(briefs: list[ScoredBrief], made: set[str]) -> int:
    """First un-made brief wins. If all made, last brief is the hero."""
    for i, b in enumerate(briefs):
        if b.brief.slot_id not in made:
            return i
    return len(briefs) - 1


def _brief_to_card(
    scored: ScoredBrief,
    made: set[str],
    slot_lookup: dict[str, Slot],
    *,
    is_hero: bool,
    locked: bool = False,
) -> dict[str, object]:
    b = scored.brief
    slot = slot_lookup.get(b.slot_id)
    return {
        "slot_id": b.slot_id,
        "pillar": slot.pillar.value if slot else None,
        "platform": slot.platform.value if slot else None,
        "format": b.format.value,
        "day": slot.day.value if slot else None,
        "daypart": slot.daypart.value if slot else None,
        "hook": b.hook,
        "outline": b.outline,
        "caption": b.caption,
        "cta": b.cta,
        "score": scored.overall,
        "fix": scored.fix,
        "made": b.slot_id in made,
        "locked": locked,
        "is_hero": is_hero,
    }


def _plan_summary(result: PipelineResult) -> dict[str, object]:
    has_dm = any(t.source.value == "dm" for t in result.audience_wants.topics)
    return {
        "goal": result.scoreboard.milestone.target,
        "milestone_description": result.scoreboard.milestone.description,
        "direction": [{"pillar": p.pillar.value, "idea": p.idea} for p in result.direction.pillars],
        "audience": {
            "source": "dm" if has_dm else "suggested",
            "topics": [t.name for t in result.audience_wants.topics],
        },
        "rhythm": [
            {
                "day": s.day.value,
                "daypart": s.daypart.value,
                "platform": s.platform.value,
                "format": s.format.value,
                "pillar": s.pillar.value,
            }
            for s in result.rhythm.slots
        ],
        "metrics": [{"name": m.name, "why": m.why} for m in result.scoreboard.metrics],
    }
