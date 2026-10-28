"""DR09 — content direction.

Type: PURE. No AI.

Contract: Strategy -> ContentDirection

Keeps only what answers "what do I create?": the lane and the three
pillars. Strips goal_type and metrics — those belong to DR12.
"""

from postwise.schemas import ContentDirection, Strategy


def build(strategy: Strategy) -> ContentDirection:
    return ContentDirection(
        lane=strategy.lane,
        pillars=list(strategy.pillar_ideas),
    )
