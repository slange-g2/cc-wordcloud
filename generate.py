#!/usr/bin/env python3
"""
generate.py — Parse Claude Code JSONL history and produce words.json for word cloud.

Reads: ~/.claude/projects/**/*.jsonl
Writes: words.json  (top 300 words, format: [["word", count], ...])
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    defaults = {
        "history_path": "~/.claude/projects",
        "palette": ["#288DFF", "#27D3BC", "#FFC800", "#FF492C", "#5746B2"],
        "excluded_words": [],
    }
    if not config_path.exists():
        return defaults
    with open(config_path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {**defaults, **data}

# ---------------------------------------------------------------------------
# Stop words
# ---------------------------------------------------------------------------

STOP_WORDS = {
    # Standard English
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know",
    "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come",
    "its", "over", "think", "also", "back", "after", "use", "two", "how",
    "our", "work", "first", "well", "way", "even", "new", "want",
    "because", "any", "these", "give", "day", "most", "us", "been", "has",
    "had", "did", "are", "was", "were", "said", "got", "here", "thing",
    "need", "let", "through", "very", "more", "may", "each", "much", "own",
    "those", "used", "using", "tell", "right", "still", "something",
    "anything", "help", "try", "going", "keep", "doesnt", "dont", "cant",
    "isnt", "youre", "thats", "its", "am", "too", "where", "who", "why",
    "off", "down", "again", "further", "then", "once", "same", "few",
    "more", "most", "other", "some", "such", "own", "so", "than", "too",
    "very", "just", "both", "while", "during", "before", "after", "above",
    "below", "between", "into", "through", "should", "must", "shall",
    "might", "need", "ought", "dare", "used", "had", "has", "have",
    "being", "done", "doing", "made", "making", "going", "gone", "given",
    "seen", "came", "come", "put", "set", "got", "getting", "making",
    "taking", "looking", "looking", "saying", "said", "know", "knew",
    "find", "found", "think", "thought", "seem", "seemed", "ask", "asked",
    "feel", "felt", "become", "became", "leave", "left", "show", "showed",
    "shown", "move", "moved", "live", "lived", "turn", "turned", "start",
    "started", "end", "ended", "point", "pointed", "play", "played",
    "run", "ran", "hold", "held", "bring", "brought", "write", "wrote",
    "stand", "stood", "hear", "heard", "let", "meet", "met", "pay", "paid",
    "sit", "sat", "speak", "spoke", "spend", "spent", "teach", "taught",
    "tell", "told", "win", "won", "understand", "understood", "watch",
    "watched", "stop", "stopped", "send", "sent", "build", "built",
    "lose", "lost", "fall", "fell", "change", "changed", "carry", "carried",
    "follow", "followed", "open", "opened", "walk", "walked",
    "provide", "provided", "include", "included", "continue", "continued",
    "create", "created", "allow", "allowed", "pass", "passed", "appear",
    "appeared", "mean", "meant", "differ", "different", "between",
    "without", "within", "against", "across", "along", "beside",
    "except", "since", "until", "while", "where", "whether", "though",
    "although", "however", "therefore", "thus", "hence", "yet", "still",
    "already", "always", "never", "ever", "often", "usually", "generally",
    "really", "quite", "pretty", "very", "rather", "fairly", "somewhat",
    "almost", "nearly", "just", "simply", "basically", "actually",
    "literally", "particularly", "especially", "specifically", "generally",
    "probably", "possibly", "perhaps", "maybe", "certainly", "definitely",
    "clearly", "obviously", "apparently", "unfortunately", "however",
    "nevertheless", "nonetheless", "furthermore", "moreover", "meanwhile",
    "instead", "otherwise", "meanwhile", "elsewhere", "somehow", "somewhat",
    "anyway", "besides", "likewise", "similarly", "consequently",
    # Contractions expanded
    "ive", "im", "id", "weve", "theyre", "hes", "shes", "were",
    "wasnt", "werent", "hadnt", "hasnt", "havent", "didnt", "doesnt",
    "wont", "wouldnt", "shouldnt", "couldnt", "mustnt", "let",
    # Short fillers
    "ok", "ah", "oh", "eh", "um", "uh", "hmm", "hm",
    # Claude-specific noise
    "claude", "please", "sure", "okay", "yes", "yep", "yeah", "nope",
    "file", "code", "check", "run", "add", "will", "look", "looks",
    "thanks", "thank", "great", "nice", "sounds", "makes", "sense",
    "feels", "actually", "basically", "literally", "simply", "really",
    "quite", "pretty", "sort", "kind", "bit", "lot", "few", "many",
    "number", "string", "value", "type", "name", "class", "function",
    "method", "object", "return", "error", "test", "true", "false",
    "null", "undefined", "const", "var", "let", "def", "import",
    "from", "export", "default",
    # Extra Claude noise
    "see", "get", "set", "use", "want", "make", "need", "put", "add",
    "now", "new", "one", "two", "three", "can", "also", "back", "just",
    "like", "work", "here", "help", "try", "right", "still", "even",
    "something", "anything", "everything", "nothing", "someone",
    "something", "somehow", "somewhere", "sometime", "sometimes",
    "everywhere", "everyone", "everything", "nobody", "nothing",
}

# ---------------------------------------------------------------------------
# Regex patterns for cleaning
# ---------------------------------------------------------------------------

# XML/HTML-like tags (strip content between angle brackets)
RE_TAGS = re.compile(r"<[^>]+>")

# URLs
RE_URL = re.compile(
    r"https?://\S+|www\.\S+",
    re.IGNORECASE,
)

# Hex strings / UUIDs (8+ consecutive hex chars)
RE_HEX = re.compile(r"\b[0-9a-f]{8,}\b", re.IGNORECASE)

# Pure numbers
RE_PURE_NUMBER = re.compile(r"^\d+$")

# Tokens that look like identifiers/paths: contain _ . / \ or are camelCase with digits
RE_IDENTIFIER_CHARS = re.compile(r"[_./\\]")

# Tokens starting with / or ~
RE_PATH_PREFIX = re.compile(r"^[/~]")


def is_noise_token(token: str) -> bool:
    """Return True if the token should be discarded."""
    # Pure number
    if RE_PURE_NUMBER.match(token):
        return True
    # Hex string (8+ hex chars)
    if RE_HEX.match(token):
        return True
    return False


def clean_text(raw: str) -> list[str]:
    """
    Clean raw text and return a list of lowercase word tokens.
    """
    text = raw

    # 1. Strip XML/HTML-like tags
    text = RE_TAGS.sub(" ", text)

    # 2. Strip URLs
    text = RE_URL.sub(" ", text)

    # 3. Lowercase
    text = text.lower()

    # 4. Split on non-alphabetic characters into tokens
    tokens = re.split(r"[^a-z]+", text)

    words = []
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        # Minimum 3 characters
        if len(tok) < 3:
            continue
        # Skip pure numbers and hex strings
        if is_noise_token(tok):
            continue
        words.append(tok)

    return words


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()
    projects_dir = Path(config["history_path"]).expanduser()
    extra_excluded = set(w.lower() for w in config.get("excluded_words", []))
    jsonl_files = sorted(projects_dir.glob("**/*.jsonl"))

    if not jsonl_files:
        print(f"No JSONL files found in {projects_dir}", file=sys.stderr)
        sys.exit(1)

    counter: Counter = Counter()
    messages_processed = 0
    parse_errors = 0

    for jsonl_path in jsonl_files:
        try:
            with open(jsonl_path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        parse_errors += 1
                        continue

                    # Filter: must be type==user AND message.role==user
                    if record.get("type") != "user":
                        continue
                    message = record.get("message", {})
                    if not isinstance(message, dict):
                        continue
                    if message.get("role") != "user":
                        continue

                    # Extract text content items
                    content = message.get("content", [])
                    if not isinstance(content, list):
                        continue

                    for item in content:
                        if not isinstance(item, dict):
                            continue
                        if item.get("type") != "text":
                            continue
                        text = item.get("text", "")
                        if not isinstance(text, str) or not text.strip():
                            continue

                        words = clean_text(text)
                        for w in words:
                            if w not in STOP_WORDS and w not in extra_excluded:
                                counter[w] += 1

                    messages_processed += 1

        except OSError as exc:
            print(f"Warning: could not read {jsonl_path}: {exc}", file=sys.stderr)

    # Apply minimum frequency filter
    filtered = {w: c for w, c in counter.items() if c >= 2}

    # Sort by frequency descending, then alphabetically for ties
    sorted_words = sorted(filtered.items(), key=lambda x: (-x[1], x[0]))

    # Top 300
    top_300 = sorted_words[:300]

    # Write words.json
    output_path = Path(__file__).parent / "words.json"
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(top_300, fh, ensure_ascii=False, indent=2)

    # Stats
    unique_words = len(filtered)
    print(f"Files scanned:       {len(jsonl_files)}")
    print(f"Messages processed:  {messages_processed}")
    print(f"Parse errors:        {parse_errors}")
    print(f"Unique words (freq≥2): {unique_words}")
    print(f"Words written:       {len(top_300)}")
    print(f"Output:              {output_path}")
    print()
    print("Top 20 words:")
    for word, count in top_300[:20]:
        print(f"  {count:>6}  {word}")


if __name__ == "__main__":
    main()
