"""The pipeline. DR00 -> DR13, in order, with a trace.

Type: ORCHESTRATOR. The only place in the codebase that imports both
postwise.dr and postwise.outputs.

Contract: (CreatorInput, LLMClient) -> PipelineResult

This file owns three things no other file does:
  1. ORDER. DR01 -> DR13 is sequential. Reordering breaks types immediately
     (DR07 needs DR06's slots, DR12 needs DR05's metrics, DR13 needs DR08's
     scored briefs).
  2. ERROR WRAPPING. Any step failure becomes PipelineError naming the step.
     Callers never see a bare traceback.
  3. TRACE. One StepRecord per step/output, so a bad plan is debuggable.

The client is INJECTED, not imported. That is what makes the whole thing
testable with FakeLLM, and swappable to a FallbackLLM wrapper later without
touching this file.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from postwise.ai.client import LLMClient
from postwise.dr import (
    dr01_check,
    dr02_understand,
    dr03_voice,
    dr04_audience,
    dr05_strategy,
    dr06_rhythm,
    dr07_write,
    dr08_score,
)
from postwise.outputs import (
    dr09_direction,
    dr10_audience,
    dr11_rhythm,
    dr12_scoreboard,
    dr13_posts,
)
from postwise.schemas import (
    Brief,
    CreatorInput,
    CreatorProfile,
    PipelineResult,
    ScoredBrief,
    StepRecord,
    Strategy,
    VoiceProfile,
)

T = TypeVar("T")


class PipelineError(RuntimeError):
    """Wraps any step failure with the step id that caused it."""

    def __init__(self, step: str, cause: BaseException) -> None:
        super().__init__(f"{step} failed: {cause}")
        self.step = step
        self.cause = cause


def run_pipeline(inp: CreatorInput, client: LLMClient) -> PipelineResult:
    trace: list[StepRecord] = []

    clean = _run_step(trace, "DR01", dr01_check.run, inp)
    profile = _run_step(
        trace,
        "DR02",
        dr02_understand.run,
        clean.input,
        client,
        prompt_version="dr02.v1",
    )
    voice = _run_step(trace, "DR03", dr03_voice.run, clean.input.samples)
    audience = _run_step(trace, "DR04", dr04_audience.run, clean.input.dm_questions, profile)
    strategy = _run_step(
        trace,
        "DR05",
        _dr05_full,
        clean.input,
        profile,
        client,
        prompt_version="dr05.v1",
    )
    rhythm_plan = _run_step(trace, "DR06", dr06_rhythm.run, clean.input)
    briefs = _run_step(
        trace,
        "DR07",
        dr07_write.run,
        rhythm_plan,
        strategy,
        profile,
        voice,
        client,
        prompt_version="dr07.v1",
    )
    scored = _run_step(trace, "DR08", _score_all, briefs, voice)

    direction = _run_step(trace, "DR09", dr09_direction.build, strategy)
    audience_wants = _run_step(trace, "DR10", dr10_audience.build, audience)
    rhythm = _run_step(trace, "DR11", dr11_rhythm.build, rhythm_plan)
    scoreboard = _run_step(trace, "DR12", dr12_scoreboard.build, strategy, clean.input)
    first_two_weeks = _run_step(trace, "DR13", dr13_posts.build, scored)

    return PipelineResult(
        direction=direction,
        audience_wants=audience_wants,
        rhythm=rhythm,
        scoreboard=scoreboard,
        briefs=first_two_weeks,
        trace=trace,
    )


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _run_step(
    trace: list[StepRecord],
    step_id: str,
    fn: Callable[..., T],
    *args: object,
    prompt_version: str | None = None,
) -> T:
    start = time.perf_counter()
    try:
        result = fn(*args)
    except Exception as e:
        elapsed = int((time.perf_counter() - start) * 1000)
        trace.append(
            StepRecord(
                dr_id=step_id,
                status="error",
                duration_ms=elapsed,
                prompt_version=prompt_version,
                note=str(e)[:200],
            )
        )
        raise PipelineError(step=step_id, cause=e) from e
    elapsed = int((time.perf_counter() - start) * 1000)
    trace.append(
        StepRecord(
            dr_id=step_id,
            status="ok",
            duration_ms=elapsed,
            prompt_version=prompt_version,
        )
    )
    return result


def _dr05_full(inp: CreatorInput, profile: CreatorProfile, client: LLMClient) -> Strategy:
    """DR05 is two halves: AI lane + code metrics. One trace entry."""
    lane = dr05_strategy.run(inp, profile, client)
    return dr05_strategy.attach_metrics(lane)


def _score_all(briefs: list[Brief], voice: VoiceProfile) -> list[ScoredBrief]:
    return [dr08_score.run(b, voice) for b in briefs]
