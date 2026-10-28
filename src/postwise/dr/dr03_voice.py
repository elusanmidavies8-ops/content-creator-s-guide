"""DR03 — measure the creator's voice.

Type: PURE. No AI, no network.

Contract: list[str] (samples) -> VoiceProfile

Measures how the creator writes or speaks. If no samples, returns a
suggested profile with source=SUGGESTED — never guesses silently.
"""

from __future__ import annotations

import re
import unicodedata

from postwise.schemas import VoiceMode, VoiceProfile, VoiceSource

SPOKEN_MARKERS = {"um", "uh", "erm", "hmm"}
FORMAL_MARKERS = {
    "however",
    "therefore",
    "regarding",
    "furthermore",
    "consequently",
    "moreover",
    "thus",
    "hence",
}
INFORMAL_MARKERS = {
    "lol",
    "lmao",
    "gonna",
    "wanna",
    "gotta",
    "yeah",
    "yep",
    "nah",
    "kinda",
    "sorta",
    "cuz",
    "coz",
    "omg",
    "tbh",
    "imo",
}
TONE_LEXICON: dict[str, set[str]] = {
    "funny": {"lol", "lmao", "haha", "🤣", "😂", "joke", "funny", "silly", "banter"},
    "serious": {"serious", "honest", "important", "critical", "reflect"},
    "energetic": {"omg", "wow", "🔥", "🚀", "excited", "let's go"},
    "calm": {"gentle", "slow", "quiet", "breathe", "steady"},
}


def run(samples: list[str]) -> VoiceProfile:
    if not samples:
        return _suggested_profile()

    text = " ".join(samples)
    return VoiceProfile(
        mode=_detect_mode(samples),
        source=VoiceSource.PASTED,
        avg_sentence_len=_avg_sentence_len(text),
        emoji_rate=_emoji_rate(text),
        formality=_formality(text),
        tone=_detect_tone(samples),
    )


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _suggested_profile() -> VoiceProfile:
    return VoiceProfile(
        mode=VoiceMode.WRITTEN,
        source=VoiceSource.SUGGESTED,
        avg_sentence_len=15.0,
        emoji_rate=0.05,
        formality=0.4,
        tone="conversational",
    )


def _avg_sentence_len(text: str) -> float:
    parts = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not parts:
        return 0.0
    return round(sum(len(p.split()) for p in parts) / len(parts), 2)


def _emoji_rate(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    emojis = sum(1 for c in text if unicodedata.category(c) == "So")
    return round(min(emojis / len(words), 1.0), 4)


def _formality(text: str) -> float:
    words = set(re.findall(r"[a-z]+", text.lower()))
    formal = len(words & FORMAL_MARKERS)
    informal = len(words & INFORMAL_MARKERS)
    total = formal + informal
    if total == 0:
        return 0.5
    return round(formal / total, 4)


def _detect_tone(samples: list[str]) -> str:
    text = " ".join(samples).lower()
    scores = {tone: sum(text.count(w) for w in words) for tone, words in TONE_LEXICON.items()}
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "conversational"


def _is_spoken(text: str) -> bool:
    if re.search(r"\b\d+:\d{2}\b", text):  # timestamp like 0:00
        return True
    words = set(re.findall(r"[a-z]+", text.lower()))
    return bool(words & SPOKEN_MARKERS)


def _detect_mode(samples: list[str]) -> VoiceMode:
    flags = [_is_spoken(s) for s in samples]
    if all(flags):
        return VoiceMode.SPOKEN
    if any(flags):
        return VoiceMode.MIXED
    return VoiceMode.WRITTEN
