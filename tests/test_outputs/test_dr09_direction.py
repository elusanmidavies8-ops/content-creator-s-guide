"""DR09 — view strips goal_type and metrics from Strategy."""

from postwise.outputs import dr09_direction
from postwise.schemas import (
    ContentDirection,
    GoalType,
    Metric,
    Pillar,
    PillarIdea,
    Strategy,
)


def _strategy() -> Strategy:
    return Strategy(
        lane="relatable comedy",
        goal_type=GoalType.AUDIENCE,
        pillar_ideas=[
            PillarIdea(pillar=Pillar.MAGNET, idea="cold open"),
            PillarIdea(pillar=Pillar.AUTHORITY, idea="breakdown"),
            PillarIdea(pillar=Pillar.AFFINITY, idea="day in life"),
        ],
        metrics=[
            Metric(name="followers", why="a"),
            Metric(name="saves", why="b"),
            Metric(name="profile visits", why="c"),
        ],
    )


def test_returns_content_direction():
    result = dr09_direction.build(_strategy())
    assert isinstance(result, ContentDirection)


def test_lane_matches_strategy():
    strategy = _strategy()
    result = dr09_direction.build(strategy)
    assert result.lane == strategy.lane


def test_pillars_match_strategy_order():
    strategy = _strategy()
    result = dr09_direction.build(strategy)
    assert result.pillars == strategy.pillar_ideas


def test_pillars_are_three():
    result = dr09_direction.build(_strategy())
    assert len(result.pillars) == 3
