"""DR04 — find what the audience wants.

Type: PURE. No AI.

Contract: (list[str] (DM questions), CreatorProfile) -> AudienceWants

Primary path: cluster DM questions by shared keywords, mark source=DM.
Fallback path: if no DMs, suggest 3 topics from the creator's niche,
marked source=SUGGESTED. Never mixes the two without labelling.
"""

from __future__ import annotations

import re

from postwise.schemas import (
    AudienceWants,
    CreatorProfile,
    Topic,
    TopicSource,
)

STOPWORDS: frozenset[str] = frozenset(
    {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "can",
        "may",
        "might",
        "must",
        "shall",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "me",
        "him",
        "her",
        "us",
        "them",
        "my",
        "your",
        "his",
        "their",
        "our",
        "this",
        "that",
        "these",
        "those",
        "what",
        "how",
        "when",
        "where",
        "why",
        "who",
        "which",
        "any",
        "some",
        "all",
        "each",
        "every",
        "no",
        "not",
        "so",
        "if",
        "then",
        "than",
        "as",
        "at",
        "by",
        "from",
        "up",
        "down",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "once",
        "here",
        "there",
        "both",
        "few",
        "more",
        "most",
        "other",
        "such",
        "nor",
        "only",
        "own",
        "same",
        "too",
        "very",
        "just",
        "also",
        "get",
        "got",
        "make",
        "made",
        "know",
        "want",
        "like",
        "please",
        "hi",
        "hello",
        "hey",
        "thanks",
        "thank",
        "tell",
        "need",
        "really",
        "actually",
    }
)
MAX_TOPICS = 5


def run(dm_questions: list[str], profile: CreatorProfile) -> AudienceWants:
    if dm_questions:
        topics = _extract_topics(dm_questions)
        if topics:
            return AudienceWants(topics=topics)
    return AudienceWants(topics=_suggest_topics(profile))


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _keywords(text: str) -> list[str]:
    words = re.findall(r"[a-z]{3,}", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _extract_topics(questions: list[str]) -> list[Topic]:
    kw_to_qs: dict[str, list[str]] = {}
    for q in questions:
        for kw in set(_keywords(q)):
            kw_to_qs.setdefault(kw, []).append(q)

    ranked = sorted(kw_to_qs.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    topics: list[Topic] = []
    for kw, qs in ranked:
        topics.append(
            Topic(
                name=kw.capitalize(),
                source=TopicSource.DM,
                examples=qs[:3],
            )
        )
        if len(topics) >= MAX_TOPICS:
            break
    return topics


def _suggest_topics(profile: CreatorProfile) -> list[Topic]:
    niche_words = [w for w in _keywords(profile.niche)][:3]
    short = " ".join(niche_words) if niche_words else "your niche"
    return [
        Topic(name=f"{short} — behind the scenes", source=TopicSource.SUGGESTED),
        Topic(name=f"{short} — beginner mistakes", source=TopicSource.SUGGESTED),
        Topic(name=f"{short} — quick tips", source=TopicSource.SUGGESTED),
    ]
