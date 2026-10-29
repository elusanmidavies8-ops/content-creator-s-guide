"""Prompt registry.

Prompts are versioned and keyed by DR id. They contain NO business logic,
no date math, no counting. They receive facts that code already measured
and return judgment.

When you change a prompt, bump the version (`dr05.v1` -> `dr05.v2`).
The FakeLLM in tests/conftest.py is keyed by prompt id, so a version bump
forces you to review the fake's canned response too.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

from postwise.schemas import Brief, CreatorProfile, StrategyLane


@dataclass(frozen=True)
class Prompt:
    system: str
    user_template: str
    output_schema: type[BaseModel]


# ---------------------------------------------------------------------------
# DR02 — profile the creator
# ---------------------------------------------------------------------------
_DR02_SYSTEM = """\
You are a content strategist. Read a beginner creator's answers and return a
short, honest profile. Four fields only: niche, audience, goal, voice_summary.
No advice. No filler. If a field is unclear, say what is most likely, not what
is possible.
"""

_DR02_USER = """\
Creator says:
- Makes and audience: {makes_and_audience}
- 90-day goal: {goal_90d}
- Hours per week: {hours_per_week}
- Audience locations: {audience_locations}
- Platforms: {platforms}
- Formats: {formats}

Return JSON matching the CreatorProfile schema.
"""


# ---------------------------------------------------------------------------
# DR05 — strategy lane (AI half only; code attaches metrics)
# ---------------------------------------------------------------------------
_DR05_SYSTEM = """\
You are a content strategist. Pick ONE lane for this creator and give exactly
three ideas: one Magnet (pulls new people in), one Authority (proves skill),
one Affinity (makes people like them). Each idea must fit the creator's niche
and the platforms they chose. No more than one sentence per idea.

Also classify the creator's goal as exactly one of:
- audience (grow followers or reach)
- community (deeper engagement, DMs, loyal fans)
- customers (turn content into sales)
- opportunities (inbound collabs, press, gigs)

Return JSON with exactly these fields:
- "lane": string (the one-sentence lane description)
- "goal_type": one of "audience", "community", "customers", "opportunities"
- "pillar_ideas": array of exactly 3 objects, each with "pillar"
  (one of "magnet", "authority", "affinity") and "idea" (string)
"""

_DR05_USER = """\
Profile:
- Niche: {niche}
- Audience: {audience}
- Goal: {goal}
- Voice: {voice_summary}

Platforms: {platforms}
Formats: {formats}

Return JSON matching the StrategyLane schema. Exactly 3 pillar ideas,
one per pillar (magnet, authority, affinity). Determine goal_type from
the goal text.
"""


# ---------------------------------------------------------------------------
# DR07 — write one brief per slot
# ---------------------------------------------------------------------------
_DR07_SYSTEM = """\
You write content briefs, not finished posts. Every brief has: hook, outline,
caption, cta.

The outline means different things by format:
- text: the outline IS the post body.
- short_video / long_video: premise and beats as a single text string. Not the performance.
- carousel: slide-by-slide outline as a single text string.
- audio: segment outline as a single text string.

IMPORTANT: The "outline" field MUST be a single string, not an object. For videos,
include both premise and beats in one string.

Use the creator's voice. Match the slot's platform and format.

Return JSON with exactly these fields:
- "slot_id": string
- "format": string (one of "text", "short_video", "long_video", "carousel", "audio")
- "hook": string
- "outline": string (single text, not an object)
- "caption": string
- "cta": string
"""

_DR07_USER = """\
Creator voice: {voice_summary}
Measured voice: avg sentence length {avg_sentence_len}, tone {tone},
formality {formality}, emoji rate {emoji_rate}.

Slot:
- Platform: {platform}
- Format: {format}
- Pillar: {pillar}
- Idea: {pillar_idea}

Write the brief. Return JSON matching the Brief schema. The outline field
must be a single string, not an object.
"""


PROMPTS: dict[str, Prompt] = {
    "dr02.v1": Prompt(
        system=_DR02_SYSTEM,
        user_template=_DR02_USER,
        output_schema=CreatorProfile,
    ),
    "dr05.v1": Prompt(
        system=_DR05_SYSTEM,
        user_template=_DR05_USER,
        output_schema=StrategyLane,
    ),
    "dr07.v1": Prompt(
        system=_DR07_SYSTEM,
        user_template=_DR07_USER,
        output_schema=Brief,
    ),
}
