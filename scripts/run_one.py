"""Full pipeline test. One CreatorInput -> complete plan."""

from postwise.ai.client import get_client
from postwise.config import get_settings
from postwise.pipeline import run_pipeline
from postwise.schemas import CreatorInput, Format, Platform

# Test input - comedy skits for Nigerian Gen Z on Instagram
test_input = CreatorInput(
    makes_and_audience="comedy skits for Nigerian Gen Z on Instagram",
    goal_90d="grow to 5,000 followers in 90 days",
    hours_per_week=5,
    audience_locations=["Nigeria", "Lagos", "Abuja"],
    platforms=[Platform.INSTAGRAM],
    formats=[Format.SHORT_VIDEO, Format.CAROUSEL],
    samples=[
        "POV: your Nigerian mom asks you to warm the stew but the gas finished",
        "When your lecturer says 'this is not a democracy' after you ask a question",
        "That one friend who pays 2k for data but uses it to watch Instagram reels",
    ],
    dm_questions=[
        "What's your biggest campus struggle right now?",
        "Which Nigerian slang do you use most?",
        "What makes you share a skit immediately?",
    ],
)

settings = get_settings()
print(f"Provider: {settings.llm_provider}")
print(f"Model: {settings.llm_model}")
print(f"API key set: {settings.llm_api_key is not None}")
print()

client = get_client(settings)

print("Running full pipeline...")
result = run_pipeline(test_input, client)

print("\n" + "=" * 60)
print("PIPELINE RESULT")
print("=" * 60)

print("\n📍 DIRECTION (DR09)")
print(f"   Lane: {result.direction.lane}")
print(f"   Pillars: {[f'{p.pillar.value}: {p.idea}' for p in result.direction.pillars]}")

print("\n👥 AUDIENCE (DR10)")
for topic in result.audience_wants.topics:
    print(f"   - {topic.name} (source: {topic.source.value})")
    if topic.examples:
        print(f"     Examples: {topic.examples}")

print("\n📅 RHYTHM (DR11)")
print(f"   Total slots: {len(result.rhythm.slots)}")
for slot in result.rhythm.slots:
    print(
        f"   - {slot.slot_id}: {slot.format.value} on "
        f"{slot.day.value} {slot.daypart.value} ({slot.platform.value})"
    )

print("\n📊 SCOREBOARD (DR12)")
print(f"   Goal type: {result.scoreboard.goal_type.value}")
print(f"   Milestone: Day {result.scoreboard.milestone.day} - {result.scoreboard.milestone.target}")
for metric in result.scoreboard.metrics:
    print(f"   - {metric.name}: {metric.why}")

print("\n📝 BRIEFS (DR13) - First 2 weeks")
for i, scored_brief in enumerate(result.briefs, 1):
    brief = scored_brief.brief
    print(f"   {i}. {brief.slot_id} [{brief.format.value}]")
    print(f"      Hook: {brief.hook}")
    print(f"      Score: {scored_brief.overall}/100")
    print(f"      Fix: {scored_brief.fix}")
    print()

print(f"\n✅ TRACE ({len(result.trace)} steps)")
for step in result.trace:
    status_emoji = "✓" if step.status == "ok" else "✗"
    print(f"   {status_emoji} {step.dr_id}: {step.status} ({step.duration_ms}ms)")
    if step.note:
        print(f"      Note: {step.note}")
