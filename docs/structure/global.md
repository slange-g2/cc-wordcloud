# Global — cc_wordcloud

## Charter
Build a word cloud visualization from the user's local Claude Code conversation history (`~/.claude/projects/**/*.jsonl`). Extract meaningful words from user messages, omit stop words and noise, and render a beautiful interactive HTML word cloud.

## Status

| Scope | Status |
|-------|--------|
| Data extraction (parse JSONL → word frequencies) | DONE |
| Word cloud visualization (HTML/JS) | DONE |

## Global rules
- Output is a self-contained `index.html` in the project root
- A `generate.py` script extracts words and writes `words.json`
- Python 3 only (no venv required — stdlib + optional `wordcloud` lib)
- Stop words: standard English stop words + Claude-specific noise (tool names, XML tags, UUIDs, code snippets)
- Extract **user messages only** from JSONL (role=user, type=user)
- Skip messages that are purely system/tool output

## Verification command
```
python3 generate.py && open index.html
```

## Source data
- Input: `~/.claude/projects/**/*.jsonl`
- JSONL structure: each line is JSON with `type`, `message.role`, `message.content[].text`
- User messages: `{"type":"user","message":{"role":"user","content":[{"type":"text","text":"..."}]}}`
