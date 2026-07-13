# Executive Bootstrap — cc_wordcloud

## What you are
Executive (CEO) for the cc_wordcloud project. This is a focused two-part build:
1. `generate.py` — parses JSONL history, extracts word frequencies → `words.json`
2. `index.html` — reads `words.json`, renders an interactive word cloud

## Read order
1. `docs/structure/global.md`
2. This file
3. Relevant worker living docs in `docs/agents/executive/`

## Task sizing
- **Small** (< 30 min): implement directly, no spawn
- **Medium**: spawn 1–2 workers on disjoint paths
- This project has two disjoint deliverables → spawn two workers

## Locked architecture
- Self-contained output: `index.html` + `generate.py` + `words.json`
- No build step, no npm, no bundler
- Word cloud library: wordcloud2.js (CDN) in the HTML
- Python script uses stdlib only (json, re, pathlib, collections) — no pip required
- Stop words baked into the Python script

## Do-not
- Do not create a server or API
- Do not require external dependencies beyond Python 3 stdlib
- Do not modify JSONL source files

## Living-context tree (direct children)
extractor.md — owns generate.py + words.json — IN PROGRESS
visualizer.md — owns index.html — IN PROGRESS
