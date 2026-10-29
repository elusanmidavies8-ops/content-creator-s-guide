"""Smoke test for the Groq client. One API call. Prints the raw profile.

If this fails, the pipeline will fail too — but with 6 layered errors
instead of one clear one. Run this first.
"""

from postwise.ai.client import get_client
from postwise.config import get_settings
from postwise.schemas import CreatorProfile

settings = get_settings()
print(f"Provider: {settings.llm_provider}")
print(f"Model: {settings.llm_model}")
print(f"API key set: {settings.llm_api_key is not None}")
print()

client = get_client(settings)

profile = client.complete_json(
    system=("You are a content strategist. Read the creator's answer and return JSON with fields: niche, audience, goal, voice_summary. Return JSON."),
    user=("Creator says: comedy skits for Nigerian Gen Z on Instagram. Goal: 5,000 followers in 90 days. Return JSON."),
    schema=CreatorProfile,
)

print("✓ Client returned a valid CreatorProfile:")
print()
print(f"  niche:         {profile.niche}")
print(f"  audience:      {profile.audience}")
print(f"  goal:          {profile.goal}")
print(f"  voice_summary: {profile.voice_summary}")
