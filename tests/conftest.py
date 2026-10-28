"""Shared fixtures. FakeLLM lets every test run offline and deterministically."""

from __future__ import annotations

from typing import TypeVar

import pytest
from pydantic import BaseModel

from postwise.schemas import (
    Brief,
    CreatorProfile,
    Format,
    GoalType,
    Pillar,
    PillarIdea,
    StrategyLane,
)

T = TypeVar("T", bound=BaseModel)


class FakeLLM:
    """Returns fixed, schema-valid objects keyed by output schema."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def complete(self, *, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        return "fake completion"

    def complete_json(self, *, system: str, user: str, schema: type[T]) -> T:
        self.calls.append({"system": system, "user": user, "schema": schema.__name__})
        return _CANNED[schema]


_CANNED: dict[type[BaseModel], BaseModel] = {
    CreatorProfile: CreatorProfile(
        niche="relatable comedy skits",
        audience="Nigerian Gen Z on Instagram and TikTok",
        goal="grow to 5,000 followers in 90 days",
        voice_summary="fast, colloquial, punchline-first",
    ),
    StrategyLane: StrategyLane(
        lane="relatable everyday comedy",
        goal_type=GoalType.AUDIENCE,
        pillar_ideas=[
            PillarIdea(pillar=Pillar.MAGNET, idea="cold open with a universal annoyance"),
            PillarIdea(pillar=Pillar.AUTHORITY, idea="break down why a viral skit works"),
            PillarIdea(pillar=Pillar.AFFINITY, idea="day-in-the-life on campus"),
        ],
    ),
    Brief: Brief(
        slot_id="mon-morning-1",
        format=Format.SHORT_VIDEO,
        hook="POV: you forgot your matric number on day one",
        outline="First day chaos. Panic. Fake confidence. Punchline.",
        caption="first day energy \U0001f602 #nigeriancomedy",
        cta="Follow for more campus chaos",
    ),
}


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()
