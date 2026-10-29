"""DR01 — validate and tidy creator input.

Type: PURE. No AI, no network, no clock.

Contract: CreatorInput -> CleanInput

The form is already validated by Pydantic (DR00). DR01's only job is to
produce non-fatal warnings for optional fields the creator skipped, so DR03
and DR04 can fall back to labelled suggestions later.
"""

from postwise.schemas import CleanInput, CreatorInput


def run(inp: CreatorInput) -> CleanInput:
    warnings: list[str] = []

    if not inp.samples:
        warnings.append("No samples pasted — DR03 will suggest a starting voice and label it as a suggestion.")

    if not inp.dm_questions:
        warnings.append("No DM questions pasted — DR04 will suggest audience topics and label them as suggestions.")

    return CleanInput(input=inp, warnings=warnings)
