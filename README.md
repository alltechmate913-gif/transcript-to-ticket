# transcript-to-ticket

Turn noisy support-call transcripts into clean deliverables: **internal notes, ticket drafts, and follow-up emails** — with PII redaction built in.

Support-call documentation is repetitive: voice-to-text transcripts can contain garbled names, phonetic spellings, and interruptions, while turning them into ticket notes by hand takes time. This tool streamlines the drafting workflow.

## Features

- **Parses** Krisp-style exports (`Speaker | 00:00` and timestamped-line formats) plus plain `Name: text` transcripts — no spoken content dropped
- **Extracts** ticket numbers, phone numbers, emails, and phonetically-spelled names (`"D is dog, O, R..."` → `DOROTHY`)
- **Drafts** internal notes / ticket drafts / follow-up emails in a consistent house style
- **Redacts** PII (emails, phones, IPs, ticket numbers) plus a custom blocklist — nothing client-specific ever leaves the machine
- **Zero dependencies** — pure Python stdlib

## Install

```bash
git clone https://github.com/<you>/transcript-to-ticket
cd transcript-to-ticket
pip install -e .
```

## Usage

```bash
# draft everything from a transcript
t2t all call.txt --property "Example Suites" --contact "Jordan Lee"

# just an internal note, with PII stripped first
t2t note call.txt --redact --blocklist clients.txt

# library use
python -c "
from transcript_to_ticket import parse, extract
t = parse(open('call.txt').read())
print(t.speakers, extract(t).ticket_numbers)
"
```

## Example

Input (synthetic):

```
Speaker 1 | 00:00
Good morning, support desk.
Alex Rivera | 00:05
Hi, this is Alex calling about ticket TICKET-20300101-0001...
```

Output (internal note):

```
**Internal Note — TICKET-20300101-0001**

Call with [confirm contact name].

Customer confirmed issue resolved on the call — ticket can be closed.

**Direct line(s) captured:** 555-010-0199

Support Agent, Support Team
```

## Design rules

- **Never invent facts.** Uncertain names/numbers are flagged (`⚠️ confirm`), not guessed.
- **Honesty by default.** Drafts document what actually happened on the call — the tool has no mode for claiming steps that weren't taken.
- **Privacy first.** `--redact` + blocklist run before any drafting; tests use only synthetic transcripts.

## Tests

```bash
python -m pytest tests/ -q
```

## License

MIT
