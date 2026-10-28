"""DR10 — what your audience wants.

Type: PURE. No AI.

Contract: AudienceWants -> AudienceWants

Pass-through today: DR04 already labels each topic as 'dm' or 'suggested'.
The module exists so DR10 is a named boundary in the pipeline; any future
view enrichment (badges, example quotes) lands here, not in DR04.
"""

from postwise.schemas import AudienceWants


def build(audience: AudienceWants) -> AudienceWants:
    return audience
