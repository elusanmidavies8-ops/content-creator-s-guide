"""Postwise data contracts.

Every shape of data in Postwise lives in this file. The DR numbers are the
spine: DR00 is CreatorInput, DR01 is CleanInput, ..., DR13 is ScoredBrief[].
Nothing in dr/, outputs/, or pipeline.py defines its own shape — they import
from here.

Two rules enforced by this file:
  1. Closed sets are StrEnum (Platform, Format, Pillar, ...) — no magic strings.
  2. Models are frozen (immutable). If a downstream step needs a different
     shape, it produces a new model; it does not mutate an existing one.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Form constants — the pitch promises 5 required + 2 optional questions.
# Tests assert against these; the Gradio form must not drift from them.
# ---------------------------------------------------------------------------
REQUIRED_QUESTION_COUNT = 5
OPTIONAL_QUESTION_COUNT = 2
MAX_SAMPLES = 3
MAX_DM_QUESTIONS = 20


# ---------------------------------------------------------------------------
# Closed sets
# ---------------------------------------------------------------------------
class Platform(StrEnum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    X = "x"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    THREADS = "threads"
    SUBSTACK = "substack"
    MEDIUM = "medium"
    BLOG = "blog"
    PODCAST = "podcast"


class Format(StrEnum):
    """Tap formats from DR00 Q5. Drives DR06 scheduling and DR07 brief shape."""

    TEXT = "text"
    SHORT_VIDEO = "short_video"
    LONG_VIDEO = "long_video"
    CAROUSEL = "carousel"
    AUDIO = "audio"


class GoalType(StrEnum):
    """Derived by DR05 from goal_90d; drives DR12 metric lookup."""

    AUDIENCE = "audience"
    COMMUNITY = "community"
    CUSTOMERS = "customers"
    OPPORTUNITIES = "opportunities"


class Pillar(StrEnum):
    """The three content buckets — the whole DR05 strategy, nothing more."""

    MAGNET = "magnet"  # pulls new people in
    AUTHORITY = "authority"  # proves the creator knows their stuff
    AFFINITY = "affinity"  # makes people like the creator


class VoiceMode(StrEnum):
    WRITTEN = "written"
    SPOKEN = "spoken"
    MIXED = "mixed"


class VoiceSource(StrEnum):
    """DR03 must always say whether a voice was measured or guessed."""

    PASTED = "pasted"
    SUGGESTED = "suggested"


class TopicSource(StrEnum):
    """DR04 must always say whether a topic came from the user or from us."""

    DM = "dm"
    SUGGESTED = "suggested"


class Daypart(StrEnum):
    """Deliberately a daypart, not a clock time. See DR06 docstring."""

    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class DayOfWeek(StrEnum):
    MON = "mon"
    TUE = "tue"
    WED = "wed"
    THU = "thu"
    FRI = "fri"
    SAT = "sat"
    SUN = "sun"


# ---------------------------------------------------------------------------
# DR00 — CreatorInput
# ---------------------------------------------------------------------------
def _strip_and_dedupe_strs(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in values:
        v = raw.strip()
        if not v or v.lower() in seen:
            continue
        seen.add(v.lower())
        out.append(v)
    return out


class CreatorInput(BaseModel):
    """DR00 — the form the creator fills in. Immutable.

    Field limits are documented where they guard a product promise
    (e.g. samples_max = 3 keeps the form under two minutes).
    """

    model_config = ConfigDict(frozen=True)

    # Q1
    makes_and_audience: str = Field(..., min_length=1, max_length=500)

    # Q2 — text answer; optional numeric target extracted by DR01 if present
    goal_90d: str = Field(..., min_length=1, max_length=300)
    goal_number: int | None = Field(default=None, gt=0, lt=100_000_000)

    # Q3
    hours_per_week: int = Field(..., ge=1, le=80)

    # Q4
    audience_locations: list[str] = Field(..., min_length=1, max_length=10)

    # Q5 — platforms AND formats, both required
    platforms: list[Platform] = Field(..., min_length=1, max_length=len(Platform))
    formats: list[Format] = Field(..., min_length=1, max_length=len(Format))

    # Q6 optional — voice source (post, caption, or transcript)
    samples: list[str] = Field(default_factory=list, max_length=MAX_SAMPLES)

    # Q7 optional — audience gaps source
    dm_questions: list[str] = Field(default_factory=list, max_length=MAX_DM_QUESTIONS)

    @field_validator("makes_and_audience", "goal_90d")
    @classmethod
    def _non_blank_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("audience_locations")
    @classmethod
    def _clean_locations(cls, v: list[str]) -> list[str]:
        cleaned = _strip_and_dedupe_strs(v)
        if not cleaned:
            raise ValueError("at least one non-blank location is required")
        for loc in cleaned:
            if len(loc) > 100:
                raise ValueError(f"location too long: {loc[:20]}…")
        return cleaned

    @field_validator("platforms", "formats")
    @classmethod
    def _dedupe_enums(cls, v: list) -> list:
        return list(dict.fromkeys(v))

    @field_validator("samples")
    @classmethod
    def _clean_samples(cls, v: list[str]) -> list[str]:
        out: list[str] = []
        for raw in v:
            s = raw.strip()
            if not s:
                continue
            if len(s) > 10_000:
                raise ValueError("each sample is capped at 10,000 characters")
            out.append(s)
        return out[:MAX_SAMPLES]

    @field_validator("dm_questions")
    @classmethod
    def _clean_dms(cls, v: list[str]) -> list[str]:
        out: list[str] = []
        for raw in v:
            s = raw.strip()
            if not s:
                continue
            if len(s) > 500:
                raise ValueError("each DM question is capped at 500 characters")
            out.append(s)
        return out[:MAX_DM_QUESTIONS]


# ---------------------------------------------------------------------------
# DR01 — CleanInput
# ---------------------------------------------------------------------------
class CleanInput(BaseModel):
    """DR01 — validated input plus non-fatal warnings (e.g. optional skipped)."""

    model_config = ConfigDict(frozen=True)

    input: CreatorInput
    warnings: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# DR02 — CreatorProfile
# ---------------------------------------------------------------------------
class CreatorProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    niche: str = Field(..., min_length=1, max_length=200)
    audience: str = Field(..., min_length=1, max_length=300)
    goal: str = Field(..., min_length=1, max_length=300)
    voice_summary: str = Field(..., min_length=1, max_length=300)


# ---------------------------------------------------------------------------
# DR03 — VoiceProfile
# ---------------------------------------------------------------------------
class VoiceProfile(BaseModel):
    """DR03 — measured from samples; never invented. `source` is mandatory."""

    model_config = ConfigDict(frozen=True)

    mode: VoiceMode
    source: VoiceSource
    avg_sentence_len: float = Field(..., ge=0.0, le=200.0)
    emoji_rate: float = Field(..., ge=0.0, le=1.0)
    formality: float = Field(..., ge=0.0, le=1.0)
    tone: str = Field(..., min_length=1, max_length=50)


# ---------------------------------------------------------------------------
# DR04 — AudienceWants
# ---------------------------------------------------------------------------
class Topic(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, max_length=100)
    source: TopicSource
    examples: list[str] = Field(default_factory=list, max_length=5)


class AudienceWants(BaseModel):
    model_config = ConfigDict(frozen=True)

    topics: list[Topic] = Field(..., min_length=1, max_length=20)


# ---------------------------------------------------------------------------
# DR05 — Strategy (hybrid: AI lane + code-selected metrics)
# ---------------------------------------------------------------------------
class PillarIdea(BaseModel):
    model_config = ConfigDict(frozen=True)

    pillar: Pillar
    idea: str = Field(..., min_length=1, max_length=500)


class Metric(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, max_length=100)
    why: str = Field(..., min_length=1, max_length=300)


class StrategyLane(BaseModel):
    """The AI-facing part of DR05. Code attaches metrics after."""

    model_config = ConfigDict(frozen=True)

    lane: str = Field(..., min_length=1, max_length=200)
    goal_type: GoalType
    pillar_ideas: list[PillarIdea] = Field(..., min_length=1, max_length=10)

    @field_validator("pillar_ideas")
    @classmethod
    def _one_per_pillar(cls, v: list[PillarIdea]) -> list[PillarIdea]:
        if len(v) != 3:
            raise ValueError("exactly 3 pillar ideas (magnet, authority, affinity)")
        if {p.pillar for p in v} != set(Pillar):
            raise ValueError("each Pillar must appear exactly once")
        return v


class Strategy(BaseModel):
    model_config = ConfigDict(frozen=True)

    lane: str
    goal_type: GoalType
    pillar_ideas: list[PillarIdea]
    metrics: list[Metric] = Field(..., min_length=3, max_length=3)


# ---------------------------------------------------------------------------
# DR06 — RhythmPlan
# ---------------------------------------------------------------------------
class Slot(BaseModel):
    """One posting slot. `daypart` is intentional — see dr06 docstring."""

    model_config = ConfigDict(frozen=True)

    slot_id: str = Field(..., min_length=1, max_length=50)
    day: DayOfWeek
    daypart: Daypart
    platform: Platform
    format: Format
    pillar: Pillar


class RhythmPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    slots: list[Slot] = Field(..., min_length=1, max_length=30)


# ---------------------------------------------------------------------------
# DR07 — Brief
# ---------------------------------------------------------------------------
class Brief(BaseModel):
    """DR07 — a brief, not a finished post.

    Shape is the same for every format, but the *meaning* of `outline` shifts:
      - text/writer:   outline is the post body.
      - video/comedian: outline is premise + beats — not the performance.
    DR07 prompts carry that framing; the schema does not need to.
    """

    model_config = ConfigDict(frozen=True)

    slot_id: str = Field(..., min_length=1, max_length=50)
    format: Format
    hook: str = Field(..., min_length=1, max_length=300)
    outline: str = Field(..., min_length=1, max_length=2_000)
    caption: str = Field(..., min_length=1, max_length=5_000)
    cta: str = Field(..., min_length=1, max_length=200)


# ---------------------------------------------------------------------------
# DR08 — ScoredBrief
# ---------------------------------------------------------------------------
class BriefSubScores(BaseModel):
    """The five named rubric criteria from the pitch. All 0-100."""

    model_config = ConfigDict(frozen=True)

    hook: float = Field(..., ge=0.0, le=100.0)
    premise: float = Field(..., ge=0.0, le=100.0)
    caption_length: float = Field(..., ge=0.0, le=100.0)
    format_fit: float = Field(..., ge=0.0, le=100.0)
    voice: float = Field(..., ge=0.0, le=100.0)


class ScoredBrief(BaseModel):
    """DR08 — one brief + its scores + exactly one specific fix."""

    model_config = ConfigDict(frozen=True)

    brief: Brief
    sub_scores: BriefSubScores
    overall: float = Field(..., ge=0.0, le=100.0)
    fix: str = Field(..., min_length=1, max_length=500)


# ---------------------------------------------------------------------------
# DR09 — ContentDirection (view over Strategy)
# ---------------------------------------------------------------------------
class ContentDirection(BaseModel):
    model_config = ConfigDict(frozen=True)

    lane: str
    pillars: list[PillarIdea] = Field(..., min_length=3, max_length=3)


# ---------------------------------------------------------------------------
# DR12 — Scoreboard
# ---------------------------------------------------------------------------
class Milestone(BaseModel):
    model_config = ConfigDict(frozen=True)

    day: int = Field(default=30, ge=1, le=90)
    target: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)


class Scoreboard(BaseModel):
    model_config = ConfigDict(frozen=True)

    goal_type: GoalType
    milestone: Milestone
    metrics: list[Metric] = Field(..., min_length=3, max_length=3)


# ---------------------------------------------------------------------------
# Pipeline envelope
# ---------------------------------------------------------------------------
class StepRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    dr_id: str = Field(..., min_length=3, max_length=4)  # "DR01" .. "DR13"
    status: Literal["ok", "warn", "error"]
    duration_ms: int = Field(..., ge=0)
    prompt_version: str | None = None
    note: str | None = None


class PipelineResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    direction: ContentDirection
    audience_wants: AudienceWants
    rhythm: RhythmPlan
    scoreboard: Scoreboard
    briefs: list[ScoredBrief]
    trace: list[StepRecord]
