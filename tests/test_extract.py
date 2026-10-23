"""Synthetic extraction cases; recognized identifiers must also redact fully."""

import pytest

from transcript_to_ticket import extract, parse, redact


@pytest.mark.parametrize("spelling, expected", [
    ("J, O, H, N", "JOHN"),
    ("J,O,H,N", "JOHN"),
    ("J O H N", "JOHN"),
    ("J-O-H-N", "JOHN"),
    ("j IS jam, o AS IN orange, h is as in hotel, n", "JOHN"),
    ("D is dog, O, R, O, T is Tom, H is Harry, Y", "DOROTHY"),
    ("J is jam, O, R is red, D is dog, A is apple, N", "JORDAN"),
])
def test_phonetic_variants(spelling, expected):
    assert extract(parse(f"Alex: My name is {spelling}.")).phonetic_spellings == [expected]


@pytest.mark.parametrize("body", [
    "Alex: A, B, C.",
    "Alex: A, B. C, D.",
    "Alex: A, B\nSam: C, D",
    "Alex: I am a caller, and I need a ticket.",
])
def test_phonetics_do_not_join_sentences_or_speakers(body):
    assert extract(parse(body)).phonetic_spellings == []


def test_phonetic_names_are_deduplicated_in_order():
    facts = extract(parse("Alex: J,O,H,N. M,A,R,Y.\nSam: J,O,H,N."))
    assert facts.phonetic_spellings == ["JOHN", "MARY"]


@pytest.mark.parametrize("phone", [
    "555-010-0199", "555.010.0199", "555 010 0199", "5550100199",
    "(555) 010-0199", "(555)010-0199", "+1 (555) 010-0199",
    "+1-555-010-0199", "1.555.010.0199", "15550100199", "+15550100199",
    "555-010-0199 ext. 42", "(555) 010-0199 x42", "5550100199 extension 42",
])
def test_phone_formats_and_redaction(phone):
    assert extract(parse(f"Alex: Call {phone}.")).phones == [phone]
    assert redact(f"Call {phone}.") == "Call [PHONE]."


@pytest.mark.parametrize("invalid", [
    "25550100199", "55501001990", "abc5550100199", "5550100199abc",
    "(555 010-0199", "555) 010-0199", "555-010-0199-1234",
])
def test_phone_does_not_extract_partial_or_malformed_number(invalid):
    assert extract(parse(f"Alex: Value {invalid}.")).phones == []


@pytest.mark.parametrize("email", [
    "a@example.com", "alex.rivera+help@example.com", "o'neil@example.com",
    "alex%help@sub-domain.example.co.uk", "ALEX@EXAMPLE.COM",
])
def test_email_formats_and_redaction(email):
    assert extract(parse(f"Alex: Email <{email}>.")).emails == [email]
    assert redact(f"Email <{email}>.") == "Email <[EMAIL]>."


@pytest.mark.parametrize("invalid", [
    "a..b@example.com", ".alex@example.com", "alex.@example.com",
    "alex@-example.com", "alex@example-.com", "alex@example..com",
    "alex@example.com-invalid", "alex@example.com@invalid.com", "alex@example.123",
])
def test_email_does_not_extract_partial_malformed_address(invalid):
    assert extract(parse(f"Alex: Email {invalid}.")).emails == []


def test_sentence_punctuation_is_not_part_of_email():
    assert extract(parse("Alex: Email a@example.com. Thanks.")).emails == ["a@example.com"]


def test_ticket_case_and_deduplication():
    facts = extract(parse("Alex: t20990101.0001, T20990101.0001; T20990101.0002."))
    assert facts.ticket_numbers == ["T20990101.0001", "T20990101.0002"]
    assert redact("t20990101.0001.") == "[TICKET]."


@pytest.mark.parametrize("invalid", [
    "XT20990101.0001", "T20990101.00010", "T20990101.0001X",
    "T20990101.0001.2", "T2099010.0001", "T２０９９０１０１.０００１",
])
def test_ticket_boundaries_and_ascii_digits(invalid):
    assert extract(parse(f"Alex: Ticket {invalid}.")).ticket_numbers == []


def test_contact_deduplication_preserves_first_seen_order():
    facts = extract(parse(
        "Alex: a@example.com b@example.com a@example.com; "
        "555-010-0199 555-010-0100 555-010-0199."
    ))
    assert facts.emails == ["a@example.com", "b@example.com"]
    assert facts.phones == ["555-010-0199", "555-010-0100"]
