"""DR07 — write one Content Brief per slot.

Type: AI. One LLM call per slot.

Contract: (RhythmPlan, Strategy, CreatorProfile, VoiceProfile, LLMClient)
          -> list[Brief]

Code overrides the slot_id on every returned brief. The AI never gets to
decide which slot a brief belongs to — that is a structural fact, not a
creative choice.
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
        briefs.append(brief.model_copy(update={"slot_id": slot.slot_id}))

    return briefs


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _find_idea(pillar: Pillar, strategy: Strategy) -> str:
    for idea in strategy.pillar_ideas:
        if idea.pillar == pillar:
            return idea.idea
    # StrategyLane validator guarantees one idea per pillar; this is unreachable.
    raise ValueError(f"no idea for pillar {pillar}")
