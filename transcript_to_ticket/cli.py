"""CLI: t2t <note|ticket|email|all> <transcript.txt> [--redact] [--blocklist terms.txt]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .drafts import ALL, DraftContext
from .extract import extract
from .parser import parse
from .redact import redact


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="t2t", description="Call transcript → support deliverables")
    p.add_argument("kind", choices=[*ALL, "all"], help="deliverable to draft")
    p.add_argument("file", type=Path, help="transcript text file")
    p.add_argument("--agent-name", default="Support Agent")
    p.add_argument("--agent-org", default="Support Team")
    p.add_argument("--property", dest="property_name", default="[confirm property name]")
    p.add_argument("--contact", dest="contact_name", default="[confirm contact name]")
    p.add_argument("--redact", action="store_true", help="strip PII before drafting")
    p.add_argument("--blocklist", type=Path, help="newline-separated terms to redact")
    args = p.parse_args(argv)

    raw = args.file.read_text(encoding="utf-8")
    if args.redact or args.blocklist:
        blocklist = (
            [ln.strip() for ln in args.blocklist.read_text().splitlines() if ln.strip()]
            if args.blocklist
            else []
        )
        raw = redact(raw, blocklist)

    t = parse(raw)
    if not t.utterances:
        print("error: no utterances parsed from transcript", file=sys.stderr)
        return 1

    f = extract(t)
    ctx = DraftContext(
        agent_name=args.agent_name,
        agent_org=args.agent_org,
        property_name=args.property_name,
        contact_name=args.contact_name,
    )

    kinds = list(ALL) if args.kind == "all" else [args.kind]
    for i, kind in enumerate(kinds):
        if i:
            print("\n---\n")
        print(ALL[kind](t, f, ctx))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
