"""DR08 — pure rubric. One fix, always."""

from postwise.dr import dr08_score
from postwise.schemas import (
    Brief,
    Format,
    ScoredBrief,
    VoiceMode,
    VoiceProfile,
    VoiceSource,
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


def _brief(
    hook: str = "POV: your first day at work",
    outline: str = "First day. Panic. Fake confidence. Punchline.",
    caption: str = "First day energy, am I right? #worklife",
) -> Brief:
    return Brief(
        slot_id="mon-morning-1",
        format=Format.SHORT_VIDEO,
        hook=hook,
        outline=outline,
        caption=caption,
        cta="Follow for more",
    )


def test_returns_scored_brief():
    result = dr08_score.run(_brief(), _voice())
    assert isinstance(result, ScoredBrief)


def test_all_sub_scores_in_range():
    result = dr08_score.run(_brief(), _voice())
    for score in (
        result.sub_scores.hook,
        result.sub_scores.premise,
        result.sub_scores.caption_length,
        result.sub_scores.format_fit,
        result.sub_scores.voice,
    ):
        assert 0.0 <= score <= 100.0


def test_overall_is_mean_of_sub_scores():
    result = dr08_score.run(_brief(), _voice())
    expected = round(
        (
            result.sub_scores.hook
            + result.sub_scores.premise
            + result.sub_scores.caption_length
            + result.sub_scores.format_fit
            + result.sub_scores.voice
        )
        / 5.0,
        2,
    )
    assert result.overall == expected


def test_fix_is_single_string():
    result = dr08_score.run(_brief(), _voice())
    assert isinstance(result.fix, str)
    assert len(result.fix) > 0
    assert result.fix.count(".") <= 2


def test_tiny_hook_lowers_hook_score():
    short = dr08_score.run(_brief(hook="POV"), _voice())
    good = dr08_score.run(_brief(hook="POV: you forgot your matric number on day one"), _voice())
    assert short.sub_scores.hook < good.sub_scores.hook


def test_tiny_caption_lowers_caption_score():
    short = dr08_score.run(_brief(caption="hi"), _voice())
    good = dr08_score.run(_brief(caption="First day energy, am I right? #worklife"), _voice())
    assert short.sub_scores.caption_length < good.sub_scores.caption_length


def test_scoring_is_deterministic():
    brief = _brief()
    voice = _voice()
    a = dr08_score.run(brief, voice)
    b = dr08_score.run(brief, voice)
    assert a.overall == b.overall
    assert a.fix == b.fix
