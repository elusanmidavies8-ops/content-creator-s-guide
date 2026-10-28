"""DR03 — pure voice measurement. No network."""

from postwise.dr import dr03_voice
from postwise.schemas import VoiceMode, VoiceSource


def test_empty_samples_returns_suggested_profile():
    profile = dr03_voice.run([])
    assert profile.source == VoiceSource.SUGGESTED
    assert profile.mode == VoiceMode.WRITTEN
    assert profile.tone == "conversational"


def test_pasted_samples_marked_as_pasted():
    profile = dr03_voice.run(["I made a quick skit today!"])
    assert profile.source == VoiceSource.PASTED


def test_long_sentences_produce_higher_avg():
    short = dr03_voice.run(["Hi. Bye. Ok."])
    long = dr03_voice.run(["When I sat down to write this post I really had no idea what to say."])
    assert long.avg_sentence_len > short.avg_sentence_len


def test_emojis_raise_emoji_rate():
    plain = dr03_voice.run(["just some words here"])
    emoji = dr03_voice.run(["just 😂 some 🤣 words 🔥 here"])
    assert emoji.emoji_rate > plain.emoji_rate


def test_informal_words_lower_formality():
    formal = dr03_voice.run(["However, therefore, we should consider."])
    informal = dr03_voice.run(["lol gonna do this tbh"])
    assert informal.formality < formal.formality


def test_spoken_marker_flips_mode():
    profile = dr03_voice.run(["um so anyway you know what I mean"])
    assert profile.mode == VoiceMode.SPOKEN


def test_mixed_spoken_and_written():
    profile = dr03_voice.run(["um here we go", "clean written post here"])
    assert profile.mode == VoiceMode.MIXED


def test_timestamp_detected_as_spoken():
    profile = dr03_voice.run(["0:00 hey guys\n0:15 so anyway"])
    assert profile.mode == VoiceMode.SPOKEN
