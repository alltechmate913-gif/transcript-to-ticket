# Contributor guide

## Project layout

- `transcript_to_ticket/parser.py`: normalize transcript formats into utterances.
- `transcript_to_ticket/extract.py`: extract facts and phonetic spellings.
- `transcript_to_ticket/patterns.py`: shared identifier regexes for extraction and redaction.
- `transcript_to_ticket/redact.py`: replace identifiers and custom blocklist terms.
- `transcript_to_ticket/drafts.py` and `cli.py`: draft templates and the `t2t` command.
- `tests/`: pytest regressions using synthetic data only.
- `examples/sample_call.txt`: synthetic CLI example.

## Setup, test, and build

Use Python 3.11 or newer. CI runs Python 3.11, 3.12, and 3.13.
The application has no runtime dependencies; pytest and build are development tools.
Run these commands from the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e . pytest build
python -m pytest tests/ -q
python -m build
t2t all examples/sample_call.txt --contact "Alex Rivera" --property "Example Suites"
```

Build artifacts go into `dist/` and are ignored by Git. To run one area while
developing, use `python -m pytest tests/test_parser.py tests/test_extract.py -q`.

## Contribution expectations

- Keep runtime code in the Python standard library and compatible with Python 3.11.
- Use type hints, small functions, and the existing dataclass models.
- Add focused regression tests for parser/extractor behavior changes, covering
  both valid input and nearby malformed input. Use only invented names and contacts.
- Preserve unstructured speech and first-seen ordering. Do not silently discard
  content when a format is unrecognized.
- Keep extraction and redaction patterns aligned; test that newly recognized
  identifiers redact completely, including country codes and extensions.
- Keep inferred spellings marked for verification. Status flags are keyword
  heuristics; do not present them as reliable natural-language understanding.
- Update README examples when supported formats or observable output change.
- Before committing, run the full pytest suite and `git diff --check`. For
  packaging changes, also build the project. Use clear, focused commit messages.
- Do not commit real transcripts, personal information, virtualenvs, or build output.
