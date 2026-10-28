"""DR07 — write one Content Brief per slot.

Type: AI. One LLM call per slot.

Contract: (RhythmPlan, Strategy, CreatorProfile, VoiceProfile, LLMClient)
          -> list[Brief]

Code overrides two fields on every returned brief:
  - slot_id: structural, not creative
  - format:  structural, not creative

The AI still decides hook, outline, caption, cta. It never decides which
slot the brief belongs to or what format it must fit — those are facts.
"""

from postwise.ai.client import LLMClient
from postwise.ai.prompts import PROMPTS
from postwise.schemas import (
    Brief,
    CreatorProfile,
    Pillar,
    RhythmPlan,
    Strategy,
    VoiceProfile,
)


def run(
    rhythm: RhythmPlan,
    strategy: Strategy,
    profile: CreatorProfile,
    voice: VoiceProfile,
    client: LLMClient,
) -> list[Brief]:
    prompt = PROMPTS["dr07.v1"]
    briefs: list[Brief] = []

    for slot in rhythm.slots:
        idea = _find_idea(slot.pillar, strategy)
        user = prompt.user_template.format(
            voice_summary=profile.voice_summary,
            avg_sentence_len=voice.avg_sentence_len,
            tone=voice.tone,
            formality=voice.formality,
            emoji_rate=voice.emoji_rate,
            platform=slot.platform.value,
            format=slot.format.value,
            pillar=slot.pillar.value,
            pillar_idea=idea,
        )
        brief = client.complete_json(
            system=prompt.system,
            user=user,
            schema=Brief,
        )
        briefs.append(brief.model_copy(update={"slot_id": slot.slot_id, "format": slot.format}))

    return briefs


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _find_idea(pillar: Pillar, strategy: Strategy) -> str:
    for idea in strategy.pillar_ideas:
        if idea.pillar == pillar:
            return idea.idea
    raise ValueError(f"no idea for pillar {pillar}")
