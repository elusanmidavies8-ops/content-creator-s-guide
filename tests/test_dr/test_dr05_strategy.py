"""DR05 — hybrid. AI lane via FakeLLM; metrics via pure code."""

from postwise.dr import dr05_strategy
from postwise.schemas import GoalType, Metric, Strategy, StrategyLane


def test_run_returns_strategy_lane(sample_input, fake_llm):
    from postwise.schemas import CreatorProfile

    profile = CreatorProfile(
        niche="comedy",
        audience="Gen Z",
        goal="5000 followers",
        voice_summary="fast",
    )
    lane = dr05_strategy.run(sample_input, profile, fake_llm)
    assert isinstance(lane, StrategyLane)
    assert len(lane.pillar_ideas) == 3


def test_run_calls_llm_once(sample_input, fake_llm):
    from postwise.schemas import CreatorProfile

    profile = CreatorProfile(niche="x", audience="y", goal="z", voice_summary="w")
    dr05_strategy.run(sample_input, profile, fake_llm)
    assert len(fake_llm.calls) == 1
    assert fake_llm.calls[0]["schema"] == "StrategyLane"


def test_attach_metrics_returns_full_strategy(fake_llm):
    lane = dr05_strategy.run(
        _dummy_input(),
        _dummy_profile(),
        fake_llm,
    )
    strategy = dr05_strategy.attach_metrics(lane)
    assert isinstance(strategy, Strategy)
    assert len(strategy.metrics) == 3
    assert all(isinstance(m, Metric) for m in strategy.metrics)


def test_attach_metrics_is_deterministic_per_goal():
    lane_audience = StrategyLane(
        lane="x",
        goal_type=GoalType.AUDIENCE,
        pillar_ideas=_three_ideas(),
    )
    a = dr05_strategy.attach_metrics(lane_audience)
    b = dr05_strategy.attach_metrics(lane_audience)
    assert [m.name for m in a.metrics] == [m.name for m in b.metrics]


def test_each_goal_type_yields_three_metrics():
    for goal in GoalType:
        lane = StrategyLane(
            lane="x",
            goal_type=goal,
            pillar_ideas=_three_ideas(),
        )
        strategy = dr05_strategy.attach_metrics(lane)
        assert len(strategy.metrics) == 3


def _dummy_input():
    from postwise.schemas import CreatorInput, Format, Platform

    return CreatorInput(
        makes_and_audience="comedy for Gen Z",
        goal_90d="grow",
        hours_per_week=6,
        audience_locations=["Nigeria"],
        platforms=[Platform.INSTAGRAM],
        formats=[Format.SHORT_VIDEO],
    )


def _dummy_profile():
    from postwise.schemas import CreatorProfile

    return CreatorProfile(niche="x", audience="y", goal="z", voice_summary="w")


def _three_ideas():
    from postwise.schemas import Pillar, PillarIdea

    return [
        PillarIdea(pillar=Pillar.MAGNET, idea="a"),
        PillarIdea(pillar=Pillar.AUTHORITY, idea="b"),
        PillarIdea(pillar=Pillar.AFFINITY, idea="c"),
    ]
