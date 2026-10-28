"""DR13 — view preserves scored briefs, exposes rescore."""

from postwise.outputs import dr13_posts
from postwise.schemas import (
    Brief,
    BriefSubScores,
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


def _brief() -> Brief:
    return Brief(
        slot_id="mon-morning-1",
        format=Format.SHORT_VIDEO,
        hook="POV: first day at work",
        outline="Panic. Fake confidence. Punchline.",
        caption="first day energy",
        cta="Follow for more",
    )


def _scored() -> ScoredBrief:
    return ScoredBrief(
        brief=_brief(),
        sub_scores=BriefSubScores(hook=80, premise=70, caption_length=90, format_fit=85, voice=75),
        overall=80,
        fix="widen the hook to 40-80 chars",
    )


def test_build_returns_list_of_scored_briefs():
    result = dr13_posts.build([_scored()])
    assert isinstance(result, list)
    assert isinstance(result[0], ScoredBrief)


def test_build_preserves_items():
    scored = _scored()
    result = dr13_posts.build([scored])
    assert result[0] == scored


def test_rescore_returns_scored_brief():
    result = dr13_posts.rescore(_brief(), _voice())
    assert isinstance(result, ScoredBrief)


def test_rescore_is_deterministic():
    brief = _brief()
    voice = _voice()
    a = dr13_posts.rescore(brief, voice)
    b = dr13_posts.rescore(brief, voice)
    assert a.overall == b.overall
    assert a.fix == b.fix
