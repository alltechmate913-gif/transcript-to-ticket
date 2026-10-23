"""Extract useful facts from a transcript: tickets, contacts, phones, emails."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .parser import Transcript

_TICKET = re.compile(r"\bT\d{8}\.\d{4}\b")
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
_PHONE = re.compile(r"\b(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")
# "T is Tom, H is Harry, Y" style phonetic spellings; a token is a bare letter
# optionally followed by "is/as in <word>"
_TOKEN = re.compile(r"\b([A-Za-z])\b(?:\s+(?:is|as in)\s+\w+)?")
# a spelling run = 4+ consecutive letter tokens separated by commas/spaces
_RUN = re.compile(r"((?:\b[A-Za-z]\b(?:\s+(?:is|as in)\s+\w+)?[,.]?\s+){4,}\b[A-Za-z]\b(?:\s+(?:is|as in)\s+\w+)?)")


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
    for run in _RUN.findall(text):
        letters = _TOKEN.findall(run)
        if len(letters) >= 4:
            out.append("".join(letters).upper())
    return out


def extract(t: Transcript) -> Facts:
    body = t.full_text
    f = Facts()
    f.ticket_numbers = list(dict.fromkeys(_TICKET.findall(body)))
    f.emails = list(dict.fromkeys(_EMAIL.findall(body)))
    f.phones = list(dict.fromkeys(_PHONE.findall(body)))
    f.phonetic_spellings = _decode_phonetic(body)
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
