"""Sanitize transcripts before they are stored, logged, or shared.

The redactor replaces common PII / confidential patterns with placeholders.
A user-supplied blocklist (client names, sites, staff names) catches the
domain-specific items a regex never will.
"""

from __future__ import annotations

import re

from .patterns import EMAIL, PHONE, TICKET

_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (TICKET, "[TICKET]"),
    (EMAIL, "[EMAIL]"),
    (PHONE, "[PHONE]"),
    (
        re.compile(
            r"\b\d{1,3}(?:\.\d{1,3}){3}\b"  # IPv4
        ),
        "[IP]",
    ),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
]


def redact(text: str, blocklist: list[str] | None = None) -> str:
    out = text
    for pattern, repl in _REPLACEMENTS:
        out = pattern.sub(repl, out)
    for term in blocklist or []:
        if not term:
            continue
        out = re.sub(re.escape(term), "[REDACTED]", out, flags=re.IGNORECASE)
    return out
