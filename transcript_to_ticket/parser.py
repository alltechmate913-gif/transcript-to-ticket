"""Parsers for common call-transcript formats.

Supports:
  * Krisp export style A: ``Speaker 1 | 00:00\\ntext``
  * Krisp export style B: ``Speaker 1\\n0:02 - text`` (line-numbered exports
    are handled by stripping leading ``N|`` prefixes first)
  * Plain ``Name: text`` lines
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Utterance:
    speaker: str
    timestamp: str | None
    text: str


@dataclass
class Transcript:
    utterances: list[Utterance] = field(default_factory=list)
    title: str = ""
    date: str = ""
    duration: str = ""

    @property
    def speakers(self) -> list[str]:
        seen: list[str] = []
        for u in self.utterances:
            if u.speaker not in seen:
                seen.append(u.speaker)
        return seen

    @property
    def full_text(self) -> str:
        return "\n".join(u.text for u in self.utterances)


_LINE_NO = re.compile(r"^\d+\|")
# Krisp A: "Speaker 1 | 00:00"
_KRISP_A = re.compile(r"^(.+?)\s*\|\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*$")
# Krisp B: "0:02 - text" (timestamp prefixed content under a speaker header)
_KRISP_B_TS = re.compile(r"^(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*(.*)$")
# "Name: text"
_NAME_COLON = re.compile(r"^([A-Z][\w .'-]{1,40}):\s+(.*)$")


def _strip_line_numbers(raw: str) -> str:
    return "\n".join(_LINE_NO.sub("", ln) for ln in raw.splitlines())


def parse(raw: str) -> Transcript:
    """Parse a transcript into structured utterances.

    The parser is tolerant: anything it cannot structure becomes part of the
    previous utterance so no spoken content is ever dropped.
    """
    text = _strip_line_numbers(raw)
    lines = [ln.rstrip() for ln in text.splitlines()]
    t = Transcript()

    # Header metadata (Krisp exports start with title / date / duration)
    i = 0
    if lines and lines[0].strip() and "meeting" in lines[0].lower():
        t.title = lines.pop(0).strip()
    if lines and re.match(r"^\w+ \d{1,2}, \d{4}", lines[0]):
        t.date = lines.pop(0).strip()
    if lines and re.match(r"^\d+m\s*\d+s$", lines[0].strip()):
        t.duration = lines.pop(0).strip()

    current: Utterance | None = None

    def flush() -> None:
        nonlocal current
        if current and current.text.strip():
            current.text = re.sub(r"\s+", " ", current.text).strip()
            t.utterances.append(current)
        current = None

    while i < len(lines):
        ln = lines[i]
        i += 1
        if not ln.strip():
            continue

        m = _KRISP_A.match(ln)
        if m:
            flush()
            current = Utterance(m.group(1).strip(), m.group(2), "")
            continue

        # Krisp B: bare speaker header, then "0:02 - text" lines
        if re.match(r"^[A-Za-z][\w .'-]{1,40}$", ln.strip()) and i < len(lines) and _KRISP_B_TS.match(lines[i]):
            flush()
            current = Utterance(ln.strip(), None, "")
            continue

        m = _KRISP_B_TS.match(ln)
        if m and current is not None:
            if current.timestamp is None:
                current.timestamp = m.group(1)
            current.text += " " + m.group(2)
            continue

        m = _NAME_COLON.match(ln)
        if m:
            flush()
            current = Utterance(m.group(1).strip(), None, m.group(2))
            continue

        # continuation text
        if current is not None:
            current.text += " " + ln.strip()

    flush()
    return t
