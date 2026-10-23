"""transcript-to-ticket: call transcripts → support deliverables."""

from .drafts import DraftContext, followup_email, internal_note, ticket_draft
from .extract import Facts, extract
from .parser import Transcript, Utterance, parse
from .redact import redact

__all__ = [
    "DraftContext",
    "Facts",
    "Transcript",
    "Utterance",
    "extract",
    "followup_email",
    "internal_note",
    "parse",
    "redact",
    "ticket_draft",
]
__version__ = "0.1.0"
