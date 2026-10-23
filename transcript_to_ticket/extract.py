"""Extract useful facts from a transcript: tickets, contacts, phones, emails."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .parser import Transcript
from .patterns import EMAIL, PHONE, TICKET

# "T is Tom, H is Harry, Y" style phonetic spellings; a token is a bare letter
# optionally followed by "is/as in <word>"
_LETTER_TOKEN = (
    r"\b([A-Za-z])\b"
    r"(?:[ \t]+(?:is(?:[ \t]+as[ \t]+in)?|as[ \t]+in)[ \t]+\w+)?"
)
_TOKEN = re.compile(_LETTER_TOKEN, re.IGNORECASE)
# a spelling run = 4+ consecutive letter tokens separated by commas/spaces
_SEPARATOR = r"(?:[ \t]*,[ \t]*|[ \t]*-[ \t]*|[ \t]+)"
_RUN = re.compile(rf"{_LETTER_TOKEN}(?:{_SEPARATOR}{_LETTER_TOKEN}){{3,}}", re.IGNORECASE)


@dataclass
class Facts:
    ticket_numbers: list[str] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    phonetic_spellings: list[str] = field(default_factory=list)
    # heuristic flags that shape the drafts
    mentions_escalation: bool = False
    mentions_resolution: bool = False
    mentions_callback: bool = False
    mentions_voicemail: bool = False


def _decode_phonetic(text: str) -> list[str]:
    """Turn "D is dog, O, R, O, T is Tom, H is Harry, Y" into DOROTHY."""
    out: list[str] = []
    for run in _RUN.finditer(text):
        letters = _TOKEN.findall(run.group())
        if len(letters) >= 4:
            out.append("".join(letters).upper())
    return out


def extract(t: Transcript) -> Facts:
    body = t.full_text
    f = Facts()
    f.ticket_numbers = list(dict.fromkeys(m.upper() for m in TICKET.findall(body)))
    f.emails = list(dict.fromkeys(EMAIL.findall(body)))
    f.phones = list(dict.fromkeys(PHONE.findall(body)))
    # Do not accidentally combine letters spoken in separate turns.
    f.phonetic_spellings = list(dict.fromkeys(
        spelling for u in t.utterances for spelling in _decode_phonetic(u.text)
    ))
    low = body.lower()
    f.mentions_escalation = any(
        k in low for k in ("escalat", "reassign", "supervisor")
    )
    f.mentions_resolution = any(
        k in low
        for k in ("resolved", "fixed", "good to go", "close the ticket", "working now")
    )
    f.mentions_callback = any(
        k in low for k in ("call back", "callback", "call you back")
    )
    f.mentions_voicemail = any(
        k in low for k in ("voicemail", "voice messaging", "leave a message", "not available")
    )
    return f
