"""DR12 — goal path and scoreboard.

Type: PURE. No AI.

Contract: (Strategy, CreatorInput) -> Scoreboard

The 30-day milestone is derived by CODE, not asked of the model. If the
creator supplied a goal_number, milestone = floor(goal_number / 3). If not,
we truncate goal_90d to fit the field limit. The three metrics were already
chosen by DR05's code (metric table lives there, not here).
"""

from postwise.schemas import CreatorInput, Milestone, Scoreboard, Strategy


def build(strategy: Strategy, inp: CreatorInput) -> Scoreboard:
    return Scoreboard(
        goal_type=strategy.goal_type,
        milestone=_build_milestone(inp),
        metrics=list(strategy.metrics),
    )


def _build_milestone(inp: CreatorInput) -> Milestone:
    if inp.goal_number is not None:
        third = max(1, inp.goal_number // 3)
        return Milestone(
            day=30,
            target=f"{third:,} by day 30",
            description=(f"A third of your 90-day target of {inp.goal_number:,}."),
        )
    return Milestone(
        day=30,
        target=inp.goal_90d[:195],
        description="Check in at day 30 against this 90-day goal.",
    )
