"""Tests use 100% synthetic transcripts — no real call content."""

from transcript_to_ticket import DraftContext, extract, parse, redact
from transcript_to_ticket.drafts import internal_note

SYNTHETIC_A = """Speaker 1 | 00:00
Good morning, support desk.
Alex Rivera | 00:05
Hi, this is Alex calling about ticket T20990101.0001.
Alex Rivera | 00:12
You can reach me at 555-010-0199 or alex.rivera@example.com.
Speaker 1 | 00:30
Thanks, it sounds like the issue is resolved then.
Alex Rivera | 00:35
Yes, it's working now, we can close the ticket.
"""

SYNTHETIC_B = """Sample meeting - January 1, 2030
January 1, 2030 9:00:00 AM
1m 18s

Speaker 1
0:02 - Thank you for calling.
Speaker 2
0:19 - Hi, my name is Jordan, J is jam, O, R is red, D is dog, A is apple, N.
Speaker 1
0:30 - Let me look at that ticket for you.
"""


def test_parse_style_a():
    t = parse(SYNTHETIC_A)
    assert len(t.utterances) == 5
    assert t.utterances[0].speaker == "Speaker 1"
    assert t.utterances[0].timestamp == "00:00"
    assert "Alex Rivera" in t.speakers


def test_parse_style_b_with_line_numbers():
    numbered = "\n".join(f"{i}|{ln}" for i, ln in enumerate(SYNTHETIC_B.splitlines(), 1))
    t = parse(numbered)
    assert t.title.startswith("Sample meeting")
    assert any(u.speaker == "Speaker 2" for u in t.utterances)
    assert any("Jordan" in u.text for u in t.utterances)


def test_extract_facts():
    f = extract(parse(SYNTHETIC_A))
    assert f.ticket_numbers == ["T20990101.0001"]
    assert f.emails == ["alex.rivera@example.com"]
    assert "555-010-0199" in f.phones
    assert f.mentions_resolution is True
    assert f.mentions_voicemail is False


def test_phonetic_spelling():
    f = extract(parse(SYNTHETIC_B))
    assert "JORDAN" in f.phonetic_spellings


def test_internal_note_marks_resolution():
    t = parse(SYNTHETIC_A)
    note = internal_note(t, extract(t), DraftContext())
    assert "T20990101.0001" in note
    assert "resolved" in note
    assert note.rstrip().endswith("Centrada Solutions")


def test_redact_strips_pii():
    dirty = "Call from T20990101.0001, phone 555-010-0199, mail a@b.com, ip 10.0.0.1"
    clean = redact(dirty)
    assert "[TICKET]" in clean and "[PHONE]" in clean
    assert "[EMAIL]" in clean and "[IP]" in clean
    assert "555-010-0199" not in clean


def test_redact_blocklist():
    out = redact("Spoke with Jordan at Example Suites about the lobby kiosk.", ["Example Suites"])
    assert "Example Suites" not in out
    assert "[REDACTED]" in out
