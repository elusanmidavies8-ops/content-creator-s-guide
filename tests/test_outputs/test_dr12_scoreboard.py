"""DR12 — milestone is derived by code from goal_number."""

from postwise.outputs import dr12_scoreboard
from postwise.schemas import (
    CreatorInput,
    Format,
    GoalType,
    Metric,
    Pillar,
    PillarIdea,
    Platform,
    Scoreboard,
    Strategy,
)


def _strategy() -> Strategy:
    return Strategy(
        lane="relatable comedy",
        goal_type=GoalType.AUDIENCE,
        pillar_ideas=[
            PillarIdea(pillar=Pillar.MAGNET, idea="a"),
            PillarIdea(pillar=Pillar.AUTHORITY, idea="b"),
            PillarIdea(pillar=Pillar.AFFINITY, idea="c"),
        ],
        metrics=[
            Metric(name="new followers per week", why="a"),
            Metric(name="saves per post", why="b"),
            Metric(name="profile visits", why="c"),
        ],
    )


def _inp(goal_number=None, goal_90d="grow to 900 followers") -> CreatorInput:
    return CreatorInput(
        makes_and_audience="comedy for Gen Z",
        goal_90d=goal_90d,
        goal_number=goal_number,
        hours_per_week=6,
        audience_locations=["Nigeria"],
        platforms=[Platform.INSTAGRAM],
        formats=[Format.SHORT_VIDEO],
    )


def test_returns_scoreboard():
    result = dr12_scoreboard.build(_strategy(), _inp())
    assert isinstance(result, Scoreboard)


def test_goal_type_matches_strategy():
    result = dr12_scoreboard.build(_strategy(), _inp())
    assert result.goal_type == GoalType.AUDIENCE


def test_metrics_come_from_strategy():
    strategy = _strategy()
    result = dr12_scoreboard.build(strategy, _inp())
    assert result.metrics == strategy.metrics


def test_milestone_with_goal_number_is_one_third():
    result = dr12_scoreboard.build(_strategy(), _inp(goal_number=900))
    assert result.milestone.day == 30
    assert result.milestone.target == "300 by day 30"


def test_milestone_without_goal_number_uses_goal_text():
    result = dr12_scoreboard.build(_strategy(), _inp(goal_90d="launch my podcast"))
    assert result.milestone.day == 30
    assert "launch my podcast" in result.milestone.target


def test_milestone_target_stays_under_field_limit():
    long_goal = "a" * 300  # goal_90d max_length
    result = dr12_scoreboard.build(_strategy(), _inp(goal_90d=long_goal))
    assert len(result.milestone.target) <= 200
