"""Chapter 7: run the Chapter 3 gates on the SFT dataset.

SFT data is training data, so it goes through the same gates as
pre-training data, in the same order:
  Chapter 2: datasheet (see datasheet_sft.md).
  Chapter 3: dedup, then PII scrub.
  Chapter 6: remember that anything repeated here can be memorized,
  and SFT data survives into the assistant.

This script checks, with the standard library only:
  1. No duplicate or near-duplicate prompts (dedup).
  2. No PII-shaped patterns: emails, phone-like numbers, long digit
     runs, URLs (scrub pre-check).
  3. No overlap between the training prompts and the held-out test
     prompts (contamination check: a test prompt that also appears
     in training is not a test).
  4. Basic counts: examples, average lengths.

It does NOT replace the Presidio scrub in Chapter 3: run pii_scrub.py
on this file too, and record the result in findings.md. A regex check
catches shapes; Presidio catches the cases a regex misses, and it
misses the cases Chapter 6 documented, so read its output as well.

Run: python dataset_checks.py
Writes: dataset_checks_report.md
"""

import json
import re

DATA_FILE = "sft_data.jsonl"
TEST_FILE = "test_prompts.jsonl"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
LONG_DIGITS_RE = re.compile(r"\d{6,}")
URL_RE = re.compile(r"https?://\S+|www\.\S+")


def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    train = load_jsonl(DATA_FILE)
    test = load_jsonl(TEST_FILE)

    lines = []
    lines.append("# SFT dataset checks (November 20, 2026 run)\n")

    # Counts.
    prompt_words = [len(r["prompt"].split()) for r in train]
    completion_words = [len(r["completion"].split()) for r in train]
    lines.append(f"Training examples: {len(train)}")
    lines.append(f"Test prompts: {len(test)}")
    lines.append(f"Average prompt length: "
                 f"{sum(prompt_words) / len(prompt_words):.1f} words")
    lines.append(f"Average completion length: "
                 f"{sum(completion_words) / len(completion_words):.1f} "
                 f"words")

    # 1. Dedup: exact duplicates, then near-duplicates (Jaccard >= 0.8).
    seen = {}
    exact_dups = []
    for i, row in enumerate(train):
        key = row["prompt"].strip().lower()
        if key in seen:
            exact_dups.append((seen[key], i, row["prompt"]))
        else:
            seen[key] = i
    near_dups = []
    for i in range(len(train)):
        for j in range(i + 1, len(train)):
            score = jaccard(words(train[i]["prompt"]),
                            words(train[j]["prompt"]))
            if score >= 0.8:
                near_dups.append((i, j, round(score, 2),
                                  train[i]["prompt"]))
    lines.append(f"\nExact duplicate prompts: {len(exact_dups)}")
    for a, b, prompt in exact_dups:
        lines.append(f"  rows {a} and {b}: {prompt!r}")
    lines.append(f"Near-duplicate prompts (Jaccard >= 0.8): "
                 f"{len(near_dups)}")
    for a, b, score, prompt in near_dups:
        lines.append(f"  rows {a} and {b} (score {score}): {prompt!r}")

    # 2. PII-shaped patterns in prompts and completions.
    hits = []
    for i, row in enumerate(train):
        for field in ("prompt", "completion"):
            text = row[field]
            for name, pattern in (("email", EMAIL_RE),
                                  ("phone-like", PHONE_RE),
                                  ("long digit run", LONG_DIGITS_RE),
                                  ("url", URL_RE)):
                m = pattern.search(text)
                if m:
                    hits.append((i, field, name, m.group(0)))
    lines.append(f"\nPII-shaped pattern hits in training data: {len(hits)}")
    for i, field, name, span in hits:
        lines.append(f"  row {i} {field}: {name} {span!r}")

    # 3. Contamination: test prompts overlapping training prompts.
    overlaps = []
    for t in test:
        for i, row in enumerate(train):
            score = jaccard(words(t["prompt"]), words(row["prompt"]))
            if score >= 0.8:
                overlaps.append((t["id"], i, round(score, 2),
                                 t["prompt"]))
    lines.append(f"\nTest prompts overlapping training prompts "
                 f"(Jaccard >= 0.8): {len(overlaps)}")
    for tid, i, score, prompt in overlaps:
        lines.append(f"  {tid} overlaps train row {i} "
                     f"(score {score}): {prompt!r}")

    report = "\n".join(lines) + "\n"
    print(report)
    with open("dataset_checks_report.md", "w") as f:
        f.write(report)
    print("Wrote dataset_checks_report.md")


if __name__ == "__main__":
    main()
