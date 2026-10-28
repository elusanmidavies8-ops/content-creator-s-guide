"""DR08 — score each brief on five named criteria and give one fix.

Type: PURE. No AI.

Contract: (Brief, VoiceProfile) -> ScoredBrief

Five criteria from the pitch: hook, premise, caption_length, format_fit,
voice. Overall = mean of the five. Fix = exactly one sentence, derived from
the lowest-scoring criterion.
"""

import re
import unicodedata

from postwise.schemas import (
    Brief,
    BriefSubScores,
    Format,
    ScoredBrief,
    VoiceProfile,
)


def run(brief: Brief, voice: VoiceProfile) -> ScoredBrief:
    sub = BriefSubScores(
        hook=_score_hook(brief.hook),
        premise=_score_premise(brief.outline),
        caption_length=_score_caption(brief.caption),
        format_fit=_score_format_fit(brief),
        voice=_score_voice(brief, voice),
    )
    overall = round(
        (sub.hook + sub.premise + sub.caption_length + sub.format_fit + sub.voice) / 5.0,
        2,
    )
    fix = _single_fix(sub, brief)
    return ScoredBrief(brief=brief, sub_scores=sub, overall=overall, fix=fix)


# ---------------------------------------------------------------------------
# Rubric
# ---------------------------------------------------------------------------
def _score_hook(hook: str) -> float:
    length = len(hook.strip())
    if length == 0:
        return 0.0
    if length < 15:
        base = 30.0
    elif length <= 50:
        base = 70.0
    elif length <= 100:
        base = 90.0
    elif length <= 200:
        base = 60.0
    else:
        base = 30.0
    if "?" in hook:
        base += 5.0
    if "POV" in hook.upper():
        base += 5.0
    return min(base, 100.0)


def _score_premise(outline: str) -> float:
    length = len(outline.strip())
    if length == 0:
        return 0.0
    if length < 30:
        return 30.0
    if length <= 200:
        return 50.0
    if length <= 500:
        return 80.0
    if length <= 1500:
        return 90.0
    return 60.0


def _score_caption(caption: str) -> float:
    length = len(caption.strip())
    if length == 0:
        return 0.0
    if length < 20:
        return 30.0
    if length < 80:
        return 60.0
    if length <= 300:
        return 90.0
    if length <= 1000:
        return 70.0
    return 40.0


def _score_format_fit(brief: Brief) -> float:
    score = 60.0
    if brief.format == Format.TEXT:
        if len(brief.outline) >= 200:
            score += 25.0
    elif brief.format in (Format.SHORT_VIDEO, Format.AUDIO):
        if 50 <= len(brief.outline) <= 800:
            score += 25.0
        if len(brief.hook) <= 100:
            score += 5.0
    elif brief.format == Format.LONG_VIDEO:
        if len(brief.outline) >= 300:
            score += 25.0
    elif brief.format == Format.CAROUSEL:
        if len(brief.outline) >= 150:
            score += 25.0
    return min(score, 100.0)


def _score_voice(brief: Brief, voice: VoiceProfile) -> float:
    text = f"{brief.hook} {brief.caption}"
    parts = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not parts:
        return 50.0
    avg = sum(len(p.split()) for p in parts) / len(parts)
    sentence_diff = abs(avg - voice.avg_sentence_len)
    score = max(0.0, 100.0 - sentence_diff * 4.0)

    emojis = sum(1 for c in text if unicodedata.category(c) == "So")
    words = len(text.split()) or 1
    brief_emoji_rate = emojis / words
    emoji_diff = abs(brief_emoji_rate - voice.emoji_rate)
    score = max(0.0, score - emoji_diff * 200.0)
    return min(score, 100.0)


def _single_fix(sub: BriefSubScores, brief: Brief) -> str:
    scores: dict[str, float] = {
        "hook": sub.hook,
        "premise": sub.premise,
        "caption_length": sub.caption_length,
        "format_fit": sub.format_fit,
        "voice": sub.voice,
    }
    worst = min(scores, key=lambda k: scores[k])
    if worst == "hook":
        return f"Hook is {len(brief.hook)} chars — aim for 40-80."
    if worst == "premise":
        return "Add one concrete beat to the outline so the premise lands."
    if worst == "caption_length":
        return f"Caption is {len(brief.caption)} chars — aim for 80-300."
    if worst == "format_fit":
        return f"Rework the brief to fit a {brief.format.value} piece."
    return "Match the creator's voice — sentence length is off."
