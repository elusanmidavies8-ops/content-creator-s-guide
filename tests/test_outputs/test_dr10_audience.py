"""DR10 — view preserves DR04's source labels."""

from postwise.outputs import dr10_audience
from postwise.schemas import AudienceWants, Topic, TopicSource


def _wants() -> AudienceWants:
    return AudienceWants(
        topics=[
            Topic(name="editing", source=TopicSource.DM, examples=["how fast?"]),
            Topic(name="behind the scenes", source=TopicSource.SUGGESTED),
        ]
    )


def test_returns_audience_wants():
    result = dr10_audience.build(_wants())
    assert isinstance(result, AudienceWants)


def test_topics_preserved():
    wants = _wants()
    result = dr10_audience.build(wants)
    assert result.topics == wants.topics


def test_source_labels_preserved():
    result = dr10_audience.build(_wants())
    sources = {t.source for t in result.topics}
    assert sources == {TopicSource.DM, TopicSource.SUGGESTED}
