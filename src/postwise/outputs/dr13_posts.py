"""DR13 — first 2 weeks of content briefs.

Type: PURE. No AI.

Contract: list[ScoredBrief] -> list[ScoredBrief], plus a rescore() helper
for the re-score button the pitch promises.

rescore() composes DR08 — that's the one place outputs/ reaches back into
dr/, because the UI action is literally "re-score this brief."
"""

from postwise.dr import dr08_score
from postwise.schemas import Brief, ScoredBrief, VoiceProfile


def build(scored_briefs: list[ScoredBrief]) -> list[ScoredBrief]:
    return list(scored_briefs)


def rescore(brief: Brief, voice: VoiceProfile) -> ScoredBrief:
    return dr08_score.run(brief, voice)
