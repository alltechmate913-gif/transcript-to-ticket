# transcript-to-ticket

Turn noisy support-call transcripts into clean deliverables: **internal notes, ticket drafts, and follow-up emails** — with PII redaction built in.

Support-call documentation is repetitive: voice-to-text transcripts can contain garbled names, phonetic spellings, and interruptions, while turning them into ticket notes by hand takes time. This tool streamlines the drafting workflow.

## Features

- **Parses** Krisp-style exports (`Speaker | 00:00` and timestamped-line formats) plus plain `Name: text` transcripts — no spoken content dropped
- **Extracts** ticket numbers, phone numbers, emails, and phonetically-spelled names (`"D is dog, O, R..."` → `DOROTHY`)
- **Drafts** internal notes / ticket drafts / follow-up emails in a consistent house style
- **Redacts** PII (emails, phones, IPs, ticket numbers) plus a custom blocklist — nothing client-specific ever leaves the machine
- **Zero runtime dependencies** — pure Python stdlib; Python 3.11+

## Install

```bash
git clone https://github.com/alltechmate913-gif/transcript-to-ticket.git
cd transcript-to-ticket
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Usage

```bash
# draft everything from a transcript
t2t all examples/sample_call.txt --property "Example Suites" --contact "Alex Rivera"

# just an internal note, with PII stripped first
t2t note call.txt --redact --blocklist clients.txt

# library use
python -c "
from transcript_to_ticket import parse, extract
from pathlib import Path
t = parse(Path('examples/sample_call.txt').read_text(encoding='utf-8'))
print(t.speakers, extract(t).ticket_numbers)
"
```

## Example

Input (synthetic):

```
Speaker 1 | 00:00
Good morning, support desk.
Alex Rivera | 00:05
Hi, this is Alex calling about ticket T20990101.0001.
Alex Rivera | 00:12
You can reach me at 555-010-0199. The issue is resolved and working now.
```

Save this as `call.txt` and run `t2t note call.txt`. Output:

```
**Internal Note — T20990101.0001**

Call with [confirm contact name].

Customer confirmed issue resolved on the call — ticket can be closed.

**Direct line(s) captured:** 555-010-0199

Support Agent, Support Team
```

## Supported formats and limits

- Transcript input supports `Speaker | 00:00`, a speaker line followed by
  `0:02 - text`, and `Name: text`. Numbered `N|` lines, CRLF, a leading UTF-8
  BOM, blank lines, and hour timestamps are accepted. Consecutive timestamped
  lines under one speaker are combined using the first timestamp.
- Leading text without a speaker is retained under `Unknown`. Whitespace is
  normalized and empty turns are omitted. A leading meeting title followed by
  a date, or a date with optional duration, is treated as export metadata.
  A bare name immediately before a timestamp is interpreted as a speaker;
  use `Name: text` if a freeform line would be ambiguous.
- Tickets use `T` plus eight digits, a dot, and four digits, such as
  `T20990101.0001`. Lowercase `t` is accepted and normalized to uppercase.
- Phones use North American ten-digit numbers, optionally prefixed by `1` or
  `+1`, with spaces, dots, hyphens, or balanced area-code parentheses. Compact
  numbers and `ext. 42`, `extension 42`, or `x42` extensions are supported.
- Emails support common ASCII addresses, including plus tags and hyphenated
  subdomains. Quoted local parts, internationalized addresses, and IP-literal
  domains are outside the supported format. Regexes do not verify ownership
  or deliverability.
- Phonetic names require at least four letters, for example `J, O, H, N` or
  `J as in jam, O, H is hotel, N` → `JOHN`. Commas, spaces, and hyphens are
  accepted; runs do not cross sentence or speaker boundaries. Short names
  and spoken NATO words without explicit letters are not decoded.

## Design rules

- **Never invent facts.** Uncertain names/numbers are flagged (`⚠️ confirm`), not guessed.
- **Review drafts before use.** Resolution, escalation, callback, and voicemail
  flags use keyword matching. They do not understand negation or hypothetical
  speech: phrases such as “not resolved” can trigger a resolution statement.
  Verify these statements against the transcript before sending or closing a ticket.
- **Privacy first.** `--redact` + blocklist run before any drafting; tests use only synthetic transcripts.

## Tests

```bash
python -m pip install pytest
python -m pytest tests/ -q
```

GitHub Actions runs the suite on Python 3.11–3.13. See [AGENTS.md](AGENTS.md)
for contributor setup, build commands, and regression-test expectations.

## License

MIT
