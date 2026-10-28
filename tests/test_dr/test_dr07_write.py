"""DR07 — one brief per slot, slot_id overridden by code."""

from postwise.dr import dr06_rhythm, dr07_write
from postwise.schemas import (
    CreatorInput,
    CreatorProfile,
    Format,
    Platform,
    VoiceMode,
    VoiceProfile,
    VoiceSource,
)


def _profile() -> CreatorProfile:
    return CreatorProfile(
        niche="comedy",
        audience="Gen Z",
        goal="5000 followers",
        voice_summary="fast, colloquial",
    )


def _voice() -> VoiceProfile:
    return VoiceProfile(
        mode=VoiceMode.WRITTEN,
        source=VoiceSource.PASTED,
        avg_sentence_len=12.0,
        emoji_rate=0.05,
        formality=0.4,
        tone="funny",
    )


def _setup(fake_llm):
    inp = CreatorInput(
        makes_and_audience="comedy for Gen Z",
        goal_90d="grow",
        hours_per_week=6,
        audience_locations=["Nigeria"],
        platforms=[Platform.INSTAGRAM],
        formats=[Format.SHORT_VIDEO],
    )
    from postwise.dr import dr05_strategy
    from postwise.schemas import GoalType, Pillar, PillarIdea, StrategyLane

    lane = StrategyLane(
        lane="comedy",
        goal_type=GoalType.AUDIENCE,
        pillar_ideas=[
            PillarIdea(pillar=Pillar.MAGNET, idea="cold open"),
            PillarIdea(pillar=Pillar.AUTHORITY, idea="breakdown"),
            PillarIdea(pillar=Pillar.AFFINITY, idea="day in life"),
        ],
    )
    strategy = dr05_strategy.attach_metrics(lane)
    rhythm = dr06_rhythm.run(inp)
    return rhythm, strategy, _profile(), _voice()


def test_one_brief_per_slot(fake_llm):
    rhythm, strategy, profile, voice = _setup(fake_llm)
    briefs = dr07_write.run(rhythm, strategy, profile, voice, fake_llm)
    assert len(briefs) == len(rhythm.slots)


def test_slot_ids_are_overridden_from_slots(fake_llm):
    rhythm, strategy, profile, voice = _setup(fake_llm)
    briefs = dr07_write.run(rhythm, strategy, profile, voice, fake_llm)
    expected = [s.slot_id for s in rhythm.slots]
    actual = [b.slot_id for b in briefs]
    assert actual == expected


def test_llm_called_once_per_slot(fake_llm):
    rhythm, strategy, profile, voice = _setup(fake_llm)
    dr07_write.run(rhythm, strategy, profile, voice, fake_llm)
    assert len(fake_llm.calls) == len(rhythm.slots)


def test_briefs_have_all_required_fields(fake_llm):
    rhythm, strategy, profile, voice = _setup(fake_llm)
    briefs = dr07_write.run(rhythm, strategy, profile, voice, fake_llm)
    for b in briefs:
        assert b.hook
        assert b.outline
        assert b.caption
        assert b.cta
