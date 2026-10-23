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


_LINE_NO = re.compile(r"^\s*\d+\s*\|\s*")
_TIMESTAMP = r"[0-9]+:[0-5][0-9](?::[0-5][0-9])?"
_SPEAKER = r"[^\W\d_][\w .’'-]{0,79}"
# Krisp A: "Speaker 1 | 00:00"
_KRISP_A = re.compile(rf"^(.+?)\s*\|\s*({_TIMESTAMP})\s*$")
# Krisp B: "0:02 - text" (timestamp prefixed content under a speaker header)
_KRISP_B_TS = re.compile(rf"^({_TIMESTAMP})\s*[-–—]\s*(.*)$")
# "Name: text"
_NAME_COLON = re.compile(rf"^({_SPEAKER}):(?!//)\s*(.*)$")
_BARE_SPEAKER = re.compile(rf"^{_SPEAKER}$")
_DATE = re.compile(
    r"^(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r" [0-9]{1,2}, [0-9]{4}(?: [0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?(?: [AP]M)?)?$",
    re.IGNORECASE,
)
_DURATION = re.compile(r"^(?:[0-9]+h\s*)?(?:[0-9]+m\s*)?[0-9]+s$")


def _strip_line_numbers(raw: str) -> str:
    return "\n".join(_LINE_NO.sub("", ln) for ln in raw.splitlines())


def parse(raw: str) -> Transcript:
    """Parse a transcript into structured utterances.

    The parser is tolerant: anything it cannot structure becomes part of the
    previous utterance. Leading unstructured content uses an ``Unknown``
    speaker. Whitespace is normalized; empty speaker turns are omitted.
    """
    text = _strip_line_numbers(raw.lstrip("\ufeff"))
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    t = Transcript()

    # Header metadata (Krisp exports start with title / date / duration)
    i = 0
    if (
        len(lines) > 1
        and "meeting" in lines[0].lower()
        and _DATE.fullmatch(lines[1])
        and not _NAME_COLON.match(lines[0])
        and not _KRISP_A.match(lines[0])
    ):
        t.title = lines.pop(0)
    if lines and _DATE.fullmatch(lines[0]):
        t.date = lines.pop(0)
        if lines and _DURATION.fullmatch(lines[0]):
            t.duration = lines.pop(0)

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
        m = _KRISP_A.match(ln)
        if m:
            flush()
            current = Utterance(m.group(1).strip(), m.group(2), "")
            continue

        # Krisp B: bare speaker header, then "0:02 - text" lines
        if (
            _BARE_SPEAKER.fullmatch(ln)
            and i < len(lines)
            and _KRISP_B_TS.match(lines[i])
        ):
            flush()
            current = Utterance(ln, None, "")
            continue

        m = _KRISP_B_TS.match(ln)
        if m:
            if current is None:
                current = Utterance("Unknown", None, "")
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
        if current is None:
            current = Utterance("Unknown", None, "")
        current.text += " " + ln

    flush()
    return t
