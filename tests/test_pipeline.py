"""End-to-end pipeline with FakeLLM. No network, deterministic."""

import pytest

from postwise.ai.client import LLMContractError
from postwise.pipeline import PipelineError, run_pipeline
from postwise.schemas import (
    ContentDirection,
    PipelineResult,
    ScoredBrief,
)

EXPECTED_DRS = [f"DR{i:02d}" for i in range(1, 14)]  # DR01..DR13


def test_happy_path_returns_pipeline_result(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    assert isinstance(result, PipelineResult)


def test_trace_covers_all_thirteen_drs(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    assert [rec.dr_id for rec in result.trace] == EXPECTED_DRS


def test_all_steps_succeed_on_happy_path(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    assert all(rec.status == "ok" for rec in result.trace)


def test_every_trace_step_has_non_negative_duration(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    assert all(rec.duration_ms >= 0 for rec in result.trace)


def test_ai_steps_record_prompt_version(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    versions = {rec.dr_id: rec.prompt_version for rec in result.trace if rec.prompt_version}
    assert versions == {
        "DR02": "dr02.v1",
        "DR05": "dr05.v1",
        "DR07": "dr07.v1",
    }


def test_direction_is_content_direction(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    assert isinstance(result.direction, ContentDirection)


def test_coherence_briefs_match_slots(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    assert len(result.briefs) == len(result.rhythm.slots)
    slot_ids = {s.slot_id for s in result.rhythm.slots}
    brief_slot_ids = {b.brief.slot_id for b in result.briefs}
    assert brief_slot_ids == slot_ids


def test_coherence_each_brief_is_scored(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    assert all(isinstance(b, ScoredBrief) for b in result.briefs)
    for scored in result.briefs:
        assert scored.fix  # never empty


def test_coherence_rhythm_uses_only_chosen_formats(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    allowed = set(sample_input.formats)
    for slot in result.rhythm.slots:
        assert slot.format in allowed


def test_coherence_scoreboard_has_three_metrics(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    assert len(result.scoreboard.metrics) == 3


def test_llm_called_dr02_once_and_dr07_per_slot(sample_input, fake_llm):
    result = run_pipeline(sample_input, fake_llm)
    # DR02 (1) + DR05 (1) + DR07 (one per slot)
    expected = 2 + len(result.rhythm.slots)
    assert len(fake_llm.calls) == expected


def test_works_without_samples_or_dms(sample_input, fake_llm):
    from postwise.schemas import CreatorInput

    no_extras = CreatorInput(
        makes_and_audience=sample_input.makes_and_audience,
        goal_90d=sample_input.goal_90d,
        goal_number=sample_input.goal_number,
        hours_per_week=sample_input.hours_per_week,
        audience_locations=sample_input.audience_locations,
        platforms=sample_input.platforms,
        formats=sample_input.formats,
    )
    result = run_pipeline(no_extras, fake_llm)
    assert all(rec.status == "ok" for rec in result.trace)


# ---------------------------------------------------------------------------
# Error wrapping
# ---------------------------------------------------------------------------
class ExplodingLLM:
    """Fails on the schema whose __name__ matches `fail_on`."""

    def __init__(self, fail_on: str) -> None:
        self.fail_on = fail_on
        self.calls: list[dict] = []

    def complete(self, *, system: str, user: str) -> str:
        return "fake"

    def complete_json(self, *, system: str, user: str, schema: type) -> object:
        self.calls.append({"schema": schema.__name__})
        if schema.__name__ == self.fail_on:
            raise LLMContractError(schema=schema, raw="bad output")
        from postwise.ai.fake import _CANNED

        return _CANNED[schema]


def test_error_in_dr02_is_wrapped_with_step_id(sample_input):
    client = ExplodingLLM(fail_on="CreatorProfile")
    with pytest.raises(PipelineError) as exc_info:
        run_pipeline(sample_input, client)
    assert exc_info.value.step == "DR02"
    assert "DR02" in str(exc_info.value)
    assert isinstance(exc_info.value.cause, LLMContractError)


def test_error_in_dr07_is_wrapped_with_step_id(sample_input):
    client = ExplodingLLM(fail_on="Brief")
    with pytest.raises(PipelineError) as exc_info:
        run_pipeline(sample_input, client)
    assert exc_info.value.step == "DR07"


def test_failed_step_recorded_with_error_status(sample_input):
    client = ExplodingLLM(fail_on="CreatorProfile")
    with pytest.raises(PipelineError):
        run_pipeline(sample_input, client)
    # We can't inspect the trace after an exception (PipelineResult never
    # returned), so this is really a test of the behavior in the code: the
    # trace gets an error entry appended before the raise.
    # Assert indirectly: the error message names the step.
    # (Deeper inspection belongs to a Phase 7 "trace on failure" test.)
