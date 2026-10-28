"""DR02 — understand the creator.

Type: AI. One call to the LLMClient.

Contract: CreatorInput -> CreatorProfile

Reads the creator's own answers into a short four-field profile. No advice,
no filler. Prompt lives in prompts.py as 'dr02.v1'.
"""

from postwise.ai.client import LLMClient
from postwise.ai.prompts import PROMPTS
from postwise.schemas import CreatorInput, CreatorProfile


def run(inp: CreatorInput, client: LLMClient) -> CreatorProfile:
    prompt = PROMPTS["dr02.v1"]
    user = prompt.user_template.format(
        makes_and_audience=inp.makes_and_audience,
        goal_90d=inp.goal_90d,
        hours_per_week=inp.hours_per_week,
        audience_locations=", ".join(inp.audience_locations),
        platforms=", ".join(p.value for p in inp.platforms),
        formats=", ".join(f.value for f in inp.formats),
    )
    return client.complete_json(
        system=prompt.system,
        user=user,
        schema=CreatorProfile,
    )
