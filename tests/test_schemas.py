"""Contract tests for every model in schemas.py.

Rule: if it's in schemas.py, it has a test here. This is what "contracts
first" means — the shapes are proven before any logic imports them.
"""

import pytest
from pydantic import ValidationError

from postwise.schemas import (
    MAX_DM_QUESTIONS,
    MAX_SAMPLES,
    OPTIONAL_QUESTION_COUNT,
    REQUIRED_QUESTION_COUNT,
    Brief,
    BriefSubScores,
    CreatorInput,
    DayOfWeek,
    Daypart,
    Format,
    GoalType,
    Metric,
    Pillar,
    PillarIdea,
    Platform,
    ScoredBrief,
    StrategyLane,
    Topic,
    TopicSource,
    VoiceMode,
    VoiceSource,
)


def make_input(**overrides) -> CreatorInput:
    base = dict(
        makes_and_audience="comedy skits for Nigerian Gen Z",
        goal_90d="grow to 5000 followers",
        goal_number=5000,
        hours_per_week=6,
        audience_locations=["Nigeria"],
        platforms=[Platform.INSTAGRAM, Platform.TIKTOK],
        formats=[Format.SHORT_VIDEO, Format.TEXT],
    )
    base.update(overrides)
    return CreatorInput(**base)


# --- form-shape invariants (the pitch's promise) --------------------------
def test_question_counts_match_pitch():
    assert REQUIRED_QUESTION_COUNT == 5
    assert OPTIONAL_QUESTION_COUNT == 2


def test_format_enum_matches_pitch_exactly():
    assert {f.value for f in Format} == {
        "text",
        "short_video",
        "long_video",
        "carousel",
        "audio",
    }


def test_pillar_enum_matches_pitch():
    assert {p.value for p in Pillar} == {"magnet", "authority", "affinity"}


def test_goal_type_enum_matches_pitch():
    assert {g.value for g in GoalType} == {
        "audience",
        "community",
        "customers",
        "opportunities",
    }


# --- DR00 CreatorInput ----------------------------------------------------
def test_valid_input_accepts():
    inp = make_input()
    assert inp.platforms == [Platform.INSTAGRAM, Platform.TIKTOK]


def test_hours_zero_rejected():
    with pytest.raises(ValidationError):
        make_input(hours_per_week=0)


def test_samples_truncated_to_three():
    inp = make_input(samples=["a"] * (MAX_SAMPLES + 3))
    assert inp.samples == ["a"] * MAX_SAMPLES


def test_empty_platforms_rejected():
    with pytest.raises(ValidationError):
        make_input(platforms=[])


def test_empty_formats_rejected():
    with pytest.raises(ValidationError):
        make_input(formats=[])


def test_blank_text_rejected():
    with pytest.raises(ValidationError):
        make_input(makes_and_audience="   ")


def test_platforms_are_deduped_preserving_order():
    inp = make_input(
        platforms=[Platform.X, Platform.INSTAGRAM, Platform.X],
    )
    assert inp.platforms == [Platform.X, Platform.INSTAGRAM]


def test_formats_are_deduped_preserving_order():
    inp = make_input(
        formats=[Format.TEXT, Format.AUDIO, Format.TEXT],
    )
    assert inp.formats == [Format.TEXT, Format.AUDIO]


def test_locations_are_stripped_and_deduped_case_insensitive():
    inp = make_input(audience_locations=[" Nigeria ", "nigeria", "Ghana"])
    assert inp.audience_locations == ["Nigeria", "Ghana"]


def test_samples_are_stripped_and_capped():
    inp = make_input(samples=["  a  ", "b", "", "c", "d", "e"])
    assert inp.samples == ["a", "b", "c"]


def test_dm_questions_are_stripped_and_capped():
    many = [f"q{i}" for i in range(MAX_DM_QUESTIONS + 5)]
    inp = make_input(dm_questions=many)
    assert len(inp.dm_questions) == MAX_DM_QUESTIONS


def test_creator_input_is_frozen():
    inp = make_input()
    with pytest.raises(ValidationError):
        inp.hours_per_week = 99  # type: ignore[misc]


# --- DR05 StrategyLane ----------------------------------------------------
def _pillar_ideas() -> list[PillarIdea]:
    return [
        PillarIdea(pillar=Pillar.MAGNET, idea="relatable cold open"),
        PillarIdea(pillar=Pillar.AUTHORITY, idea="breakdown of a viral skit"),
        PillarIdea(pillar=Pillar.AFFINITY, idea="day-in-the-life"),
    ]


def test_strategy_lane_requires_exactly_one_idea_per_pillar():
    with pytest.raises(ValidationError):
        StrategyLane(
            lane="relatable comedy",
            goal_type=GoalType.AUDIENCE,
            pillar_ideas=_pillar_ideas()[:2],
        )


def test_strategy_lane_rejects_duplicate_pillar():
    dup = _pillar_ideas()
    dup[2] = PillarIdea(pillar=Pillar.MAGNET, idea="dup")
    with pytest.raises(ValidationError):
        StrategyLane(lane="x", goal_type=GoalType.AUDIENCE, pillar_ideas=dup)


# --- DR07 / DR08 ----------------------------------------------------------
def test_brief_requires_caption_and_cta():
    with pytest.raises(ValidationError):
        Brief(
            slot_id="mon-morning-1",
            format=Format.SHORT_VIDEO,
            hook="hook",
            outline="outline",
            caption="",
            cta="cta",
        )


def test_scored_brief_has_exactly_one_fix():
    brief = Brief(
        slot_id="mon-morning-1",
        format=Format.SHORT_VIDEO,
        hook="h",
        outline="o",
        caption="c",
        cta="cta",
    )
    scored = ScoredBrief(
        brief=brief,
        sub_scores=BriefSubScores(hook=80, premise=70, caption_length=90, format_fit=85, voice=75),
        overall=80,
        fix="tighten the hook to first 3 words",
    )
    assert isinstance(scored.fix, str)  # not a list — enforced by schema


# --- DR04 Topic -----------------------------------------------------------
def test_topic_source_is_required():
    with pytest.raises(ValidationError):
        Topic(name="behind the scenes", examples=["q1"])  # type: ignore[call-arg]


def test_topic_source_enum_covers_dm_and_suggested():
    assert {s.value for s in TopicSource} == {"dm", "suggested"}


# --- DR03 VoiceProfile enums ---------------------------------------------
def test_voice_mode_and_source_enums():
    assert {m.value for m in VoiceMode} == {"written", "spoken", "mixed"}
    assert {s.value for s in VoiceSource} == {"pasted", "suggested"}


# --- DR06 Slot / DR12 Metric ---------------------------------------------
def test_daypart_and_day_enums_exist():
    assert {d.value for d in Daypart} == {"morning", "afternoon", "evening"}
    assert {d.value for d in DayOfWeek} == {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}


def test_metric_shape():
    m = Metric(name="saves", why="saves are the cheapest signal of value")
    assert m.name == "saves"
