"""Shared fixtures. FakeLLM lives in postwise.ai.fake so it's importable
from scripts and the Gradio app, not just from pytest."""

from __future__ import annotations

import pytest

from postwise.ai.fake import FakeLLM
from postwise.schemas import CreatorInput, Format, Platform


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def sample_input() -> CreatorInput:
    return CreatorInput(
        makes_and_audience="comedy skits for Nigerian Gen Z",
        goal_90d="grow to 5000 followers",
        goal_number=5000,
        hours_per_week=6,
        audience_locations=["Nigeria"],
        platforms=[Platform.INSTAGRAM, Platform.TIKTOK],
        formats=[Format.SHORT_VIDEO, Format.TEXT],
    )