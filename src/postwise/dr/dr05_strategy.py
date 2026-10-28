"""DR05 — build the strategy.

Type: HYBRID. AI picks lane + goal_type + 3 pillar ideas; code picks metrics.

Contract: (CreatorInput, CreatorProfile) -> Strategy

Two public functions:
  - run(input, profile, client): the AI half; returns StrategyLane
  - attach_metrics(lane): the code half; returns full Strategy

The metric table lives in this file, not in the prompt. Same goal_type
must always produce the same three metrics. That is the "transparent"
promise in the pitch.
"""

from postwise.ai.client import LLMClient
from postwise.ai.prompts import PROMPTS
from postwise.schemas import (
    CreatorInput,
    CreatorProfile,
    GoalType,
    Metric,
    Strategy,
    StrategyLane,
)

_METRICS_BY_GOAL: dict[GoalType, list[Metric]] = {
    GoalType.AUDIENCE: [
        Metric(name="new followers per week", why="signals reach expanding"),
        Metric(name="saves per post", why="saves are the strongest signal of value"),
        Metric(name="profile visits", why="people who want to see more"),
    ],
    GoalType.COMMUNITY: [
        Metric(name="DM replies", why="one-to-one conversations signal trust"),
        Metric(name="comments per post", why="public conversation signal"),
        Metric(name="returning viewers", why="people coming back by name"),
    ],
    GoalType.CUSTOMERS: [
        Metric(name="link clicks", why="interest you can measure"),
        Metric(name="inquiries or price DMs", why="intent to buy"),
        Metric(name="email signups", why="owned-audience growth"),
    ],
    GoalType.OPPORTUNITIES: [
        Metric(name="brand or collab DMs", why="inbound opportunity"),
        Metric(name="press or feature mentions", why="external validation"),
        Metric(name="speaking or podcast invites", why="platform expansion"),
    ],
}


def run(inp: CreatorInput, profile: CreatorProfile, client: LLMClient) -> StrategyLane:
    prompt = PROMPTS["dr05.v1"]
    user = prompt.user_template.format(
        niche=profile.niche,
        audience=profile.audience,
        goal=profile.goal,
        voice_summary=profile.voice_summary,
        platforms=", ".join(p.value for p in inp.platforms),
        formats=", ".join(f.value for f in inp.formats),
    )
    return client.complete_json(
        system=prompt.system,
        user=user,
        schema=StrategyLane,
    )


def attach_metrics(lane: StrategyLane) -> Strategy:
    """The pure half. Same goal_type always yields the same 3 metrics."""
    return Strategy(
        lane=lane.lane,
        goal_type=lane.goal_type,
        pillar_ideas=lane.pillar_ideas,
        metrics=list(_METRICS_BY_GOAL[lane.goal_type]),
    )
