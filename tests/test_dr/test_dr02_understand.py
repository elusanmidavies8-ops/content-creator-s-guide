"""DR02 — one LLM call, returns a CreatorProfile."""

from postwise.dr import dr02_understand
from postwise.schemas import CreatorProfile


def test_returns_creator_profile(sample_input, fake_llm):
    profile = dr02_understand.run(sample_input, fake_llm)
    assert isinstance(profile, CreatorProfile)
    assert profile.niche
    assert profile.audience
    assert profile.goal
    assert profile.voice_summary


def test_calls_llm_exactly_once(sample_input, fake_llm):
    dr02_understand.run(sample_input, fake_llm)
    assert len(fake_llm.calls) == 1
    assert fake_llm.calls[0]["schema"] == "CreatorProfile"


def test_user_message_includes_creator_answers(sample_input, fake_llm):
    dr02_understand.run(sample_input, fake_llm)
    sent = fake_llm.calls[0]["user"]
    assert "Nigerian Gen Z" in sent
    assert "5000" in sent or "5,000" in sent or "5000 followers" in sent
    assert "instagram" in sent
