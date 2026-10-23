"""Generate deliverables: internal note, ticket draft, follow-up email.

Templates follow a "house style": short, concise, honest. Every fact in the
output must trace back to the transcript; uncertain items are flagged, never
invented.
"""

from __future__ import annotations

from dataclasses import dataclass

from .extract import Facts
from .parser import Transcript


@dataclass
class DraftContext:
    agent_name: str = "Support Agent"
    agent_org: str = "Support Team"
    property_name: str = "[confirm property name]"
    contact_name: str = "[confirm contact name]"


def _flagged(value: str) -> str:
    known = not value.startswith("[confirm")
    return value if known else f"{value} ⚠️ (confirm — garbled in transcript)"


def internal_note(t: Transcript, f: Facts, ctx: DraftContext) -> str:
    lines = [f"**Internal Note{f' — {f.ticket_numbers[0]}' if f.ticket_numbers else ''}**", ""]
    if f.mentions_voicemail:
        lines.append("Outbound call to contact — reached voicemail, left callback message.")
    else:
        lines.append(f"Call with {ctx.contact_name}.")
    if f.mentions_escalation:
        lines.append("")
        lines.append("**Customer requested escalation / reassignment.**")
    if f.mentions_resolution:
        lines.append("")
        lines.append("Customer confirmed issue resolved on the call — ticket can be closed.")
    if f.phones:
        lines.append("")
        lines.append(f"**Direct line(s) captured:** {', '.join(f.phones)}")
    if f.phonetic_spellings:
        lines.append("")
        lines.append(
            "**Names spelled phonetically on call:** "
            + ", ".join(f.phonetic_spellings)
            + " ⚠️ (verify against account)"
        )
    lines += ["", f"{ctx.agent_name}, {ctx.agent_org}"]
    return "\n".join(lines)


def ticket_draft(t: Transcript, f: Facts, ctx: DraftContext) -> str:
    return "\n".join(
        [
            "**Support Ticket Draft**",
            "",
            f"**Account:** {_flagged(ctx.property_name)}",
            f"**Contact:** {_flagged(ctx.contact_name)}",
            "**Issue Type:** [set from your ticketing system]",
            "**Priority:** [1-High if urgent / 3-Medium default]",
            "**Source:** Phone",
            "",
            "**Description:**",
            "",
            "[Summarize the issue in 2-4 sentences from the transcript.]",
            "",
            "**Troubleshooting steps taken:**",
            "[List only steps actually performed on the call.]",
            "",
            f"{ctx.agent_name}, {ctx.agent_org}",
        ]
    )


def followup_email(t: Transcript, f: Facts, ctx: DraftContext) -> str:
    subject = (
        f"Follow-up — {f.ticket_numbers[0]}" if f.ticket_numbers else "Follow-up on your request"
    )
    return "\n".join(
        [
            f"Subject: {subject}",
            "",
            f"Hi {ctx.contact_name.split()[0] if ctx.contact_name != '[confirm contact name]' else 'there'},",
            "",
            "Thanks for your time today. [One sentence: current status / next step.]",
            "",
            "If anything changes in the meantime, just reply to this email or give us a call.",
            "",
            "Thank you,",
            ctx.agent_name,
            ctx.agent_org,
        ]
    )


ALL = {
    "note": internal_note,
    "ticket": ticket_draft,
    "email": followup_email,
}
