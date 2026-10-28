"""Render contract. This shape is what the UI consumes."""

import pytest

from postwise import state
from postwise.pipeline import run_pipeline
from postwise.render import build_view
from postwise.schemas import PipelineResult


@pytest.fixture(autouse=True)
def _clean_sessions() -> None:
    state.reset("test-session")
    yield
    state.reset("test-session")


@pytest.fixture
def result(sample_input, fake_llm) -> PipelineResult:
    return run_pipeline(sample_input, fake_llm)


def test_view_has_all_top_level_keys(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    assert set(view.keys()) == {
        "session_id",
        "lane",
        "hero",
        "queue",
        "progress",
        "plan",
    }


def test_lane_is_populated(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    assert isinstance(view["lane"], str)
    assert view["lane"]


def test_hero_is_first_brief(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    assert view["hero"] is not None
    assert view["hero"]["is_hero"] is True
    assert view["hero"]["slot_id"] == result.briefs[0].brief.slot_id


def test_hero_has_all_card_fields(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    card = view["hero"]
    required = {
        "slot_id",
        "pillar",
        "platform",
        "format",
        "day",
        "daypart",
        "hook",
        "outline",
        "caption",
        "cta",
        "score",
        "fix",
        "made",
        "locked",
        "is_hero",
    }
    for key in required:
        assert key in card, f"missing card field: {key}"


def test_queue_has_rest_of_briefs(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    assert len(view["queue"]) == len(result.briefs) - 1


def test_queue_items_are_locked(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    for card in view["queue"]:
        assert card["locked"] is True


def test_progress_starts_at_zero(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    assert view["progress"] == {
        "made": 0,
        "total": len(result.briefs),
        "ratio": 0.0,
    }


def test_marking_made_advances_hero(result: PipelineResult) -> None:
    view1 = build_view(result, "test-session")
    first_slot = view1["hero"]["slot_id"]
    state.mark_made("test-session", first_slot)
    view2 = build_view(result, "test-session")
    assert view2["progress"]["made"] == 1
    assert view2["hero"]["slot_id"] != first_slot


def test_all_made_keeps_last_as_hero(result: PipelineResult) -> None:
    for b in result.briefs:
        state.mark_made("test-session", b.brief.slot_id)
    view = build_view(result, "test-session")
    assert view["progress"]["made"] == len(result.briefs)
    assert view["hero"] is not None


def test_plan_summary_has_all_sections(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    plan = view["plan"]
    assert len(plan["direction"]) == 3
    assert plan["audience"]["source"] in ("dm", "suggested")
    assert len(plan["audience"]["topics"]) > 0
    assert len(plan["rhythm"]) == len(result.rhythm.slots)
    assert len(plan["metrics"]) == 3


def test_multi_platform_and_multi_format_cards(result: PipelineResult) -> None:
    view = build_view(result, "test-session")
    all_cards = [view["hero"], *view["queue"]]
    platforms = {c["platform"] for c in all_cards}
    formats = {c["format"] for c in all_cards}
    assert len(platforms) == 2
    assert len(formats) == 2
