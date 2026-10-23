"""Synthetic transcript format and content-preservation regressions."""

import pytest

from transcript_to_ticket import parse


@pytest.mark.parametrize("raw", ["", " \n\t", "\ufeff\r\n"])
def test_empty_transcript(raw):
    assert parse(raw).utterances == []


def test_unstructured_content_is_preserved():
    t = parse("Please help with the kiosk.\nIt is offline.\nAlex: Checking now.")
    assert t.speakers == ["Unknown", "Alex"]
    assert t.utterances[0].text == "Please help with the kiosk. It is offline."


@pytest.mark.parametrize("raw", [
    "We had a meeting about the kiosk.",
    "Alex: The meeting starts soon.",
    "2m 30s",
    "January 1, 2030 was when it broke.",
])
def test_speech_is_not_mistaken_for_metadata(raw):
    t = parse(raw)
    assert t.title == t.date == t.duration == ""
    assert t.full_text == raw.removeprefix("Alex: ")


def test_bom_crlf_indentation_and_blank_metadata_lines():
    t = parse(
        "\ufeff\r\n  Sample meeting\r\n\r\nJanuary 1, 2030 9:00:00 AM\r\n"
        "\r\n1h 2m 3s\r\n\r\n  Alex | 01:02:03\r\n  Hello.\r\n"
    )
    assert (t.title, t.date, t.duration) == (
        "Sample meeting", "January 1, 2030 9:00:00 AM", "1h 2m 3s",
    )
    assert (t.utterances[0].speaker, t.utterances[0].timestamp, t.full_text) == (
        "Alex", "01:02:03", "Hello.",
    )


def test_numbered_style_b_with_blank_lines_and_unicode_dashes():
    t = parse(" 1 | Élodie\n 2 |\n 3 | 0:02 – Hello.\n 4 | 0:05 — Still here.")
    assert t.speakers == ["Élodie"]
    assert t.utterances[0].timestamp == "0:02"
    assert t.full_text == "Hello. Still here."


@pytest.mark.parametrize("speaker", ["a", "A", "alex", "Élodie", "李", "O’Neil"])
def test_plain_speaker_names_and_no_space_after_colon(speaker):
    t = parse(f"{speaker}:Hello.\nA continuation.")
    assert t.speakers == [speaker]
    assert t.full_text == "Hello. A continuation."


def test_empty_plain_header_and_empty_turns():
    t = parse("Alex:\nHello.\nSam | 00:01\nJo | 00:02\nGoodbye.")
    assert t.speakers == ["Alex", "Jo"]
    assert t.full_text == "Hello.\nGoodbye."


def test_timestamp_without_speaker():
    t = parse("100:02 - Hello.\n100:03 - Still here.")
    assert t.speakers == ["Unknown"]
    assert t.utterances[0].timestamp == "100:02"
    assert t.full_text == "Hello. Still here."


def test_url_continuation_does_not_become_speaker():
    t = parse("Alex: Visit this link:\nhttps://example.com/help")
    assert t.speakers == ["Alex"]
    assert t.full_text.endswith("https://example.com/help")


def test_mixed_formats_preserve_speaker_order():
    t = parse("Alex | 00:00\nHello.\nSam\n0:02 - Hi.\nAlex: Goodbye.")
    assert t.speakers == ["Alex", "Sam"]
    assert len(t.utterances) == 3


def test_invalid_timestamp_is_retained_as_text():
    t = parse("Alex: Checking.\n00:99 - Invalid time.")
    assert t.full_text == "Checking. 00:99 - Invalid time."
