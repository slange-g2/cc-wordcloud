# Worker: Data Extractor
Path: docs/agents/executive/extractor.md | Last updated: 2026-07-13 | Tasks: generate.py + words.json

## Purpose & scope boundary
Write `generate.py` in the project root. It scans all `~/.claude/projects/**/*.jsonl` files, extracts text from user messages, computes word frequencies, and writes `words.json`.

**In scope:** generate.py, words.json output format
**Out of scope:** index.html, visualization, CSS

## State of the work
DONE — generate.py written and verified 2026-07-13.
- Scanned 130 JSONL files, processed 9 059 user messages, 0 parse errors.
- 2 497 unique words with frequency ≥ 2; top 300 written to words.json.
- words.json format confirmed: `[["word", count], ...]` sorted by count descending.

## Decisions in force
- Python 3 stdlib only (json, re, pathlib, collections.Counter)
- Extract only lines where `type == "user"` and `message.role == "user"`
- From each such line, read all `message.content[].text` strings
- Minimum word length: 3 chars
- Minimum frequency: 2 occurrences (suppress hapax legomena)
- `words.json` format: `[["word", count], ...]` sorted by count descending, top 300 words
- wordcloud2.js expects exactly this format

## Stop words to exclude
Standard English stop words PLUS:
- Claude-specific: "claude", "please", "can", "could", "would", "like", "just", "also", "use", "used", "using", "make", "need", "want", "let", "tell", "think", "know", "look", "looks", "here", "there", "okay", "yes", "the", "sure", "add", "will", "file", "code", "check", "get", "run", "one", "new", "see", "help", "try", "work", "right", "now", "still", "even", "something", "anything", "everything", "nothing"
- Skip tokens that look like: UUIDs (8+ hex chars), file paths (/Users/...), XML/HTML tags, URLs, numbers-only

## Open decisions
None.

## Gotchas
- Some JSONL lines are queue-operation or other types — skip them
- message.content is an array; iterate all items and check type == "text"
- Some text content wraps XML-like tags (e.g., `<ide_opened_file>`) — strip them
- User messages often paste code — strip code-like tokens (camelCase, underscores, dots in identifiers)
