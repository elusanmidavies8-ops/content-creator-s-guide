"""DR04 — pure topic extraction. Fallback is labelled, never silent."""

from postwise.dr import dr04_audience
from postwise.schemas import CreatorProfile, TopicSource


def _profile(niche: str = "relatable comedy skits") -> CreatorProfile:
    return CreatorProfile(
        niche=niche,
        audience="Nigerian Gen Z",
        goal="5000 followers",
        voice_summary="fast, colloquial",
    )


def test_no_dms_gives_suggested_topics():
    wants = dr04_audience.run([], _profile())
    assert len(wants.topics) == 3
    assert all(t.source == TopicSource.SUGGESTED for t in wants.topics)


def test_suggested_topics_reference_niche():
    wants = dr04_audience.run([], _profile(niche="campus comedy skits"))
    joined = " ".join(t.name for t in wants.topics).lower()
    assert "campus" in joined or "comedy" in joined or "skits" in joined


def test_dm_questions_produce_dm_topics():
    dms = [
        "how do you edit your skits so fast",
        "your skit editing is so clean",
        "what camera do you use for skits",
    ]
    wants = dr04_audience.run(dms, _profile())
    assert wants.topics
    assert all(t.source == TopicSource.DM for t in wants.topics)


def test_topics_include_examples_from_dms():
    dms = ["how do you edit skits", "your skits are great"]
    wants = dr04_audience.run(dms, _profile())
    assert any(t.examples for t in wants.topics)


def test_topics_capped_at_five():
    dms = [f"random question number {i} about skits" for i in range(20)]
    wants = dr04_audience.run(dms, _profile())
    assert len(wants.topics) <= 5


def test_dms_with_no_keywords_falls_back_to_suggested():
    wants = dr04_audience.run(["hi", "ok", "the"], _profile())
    assert wants.topics
    assert all(t.source == TopicSource.SUGGESTED for t in wants.topics)
