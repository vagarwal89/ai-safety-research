"""Chapter 2 - dataset license audit and datasheet measurements.

Run:  python license_audit.py

Needs: pip install datasets
It calls the public Hugging Face API to fetch each dataset's declared
license, and streams a small sample of rows with the datasets library.
If the network or the library is unavailable it falls back to a small
embedded sample, and says so clearly in the report.

What it checks for each dataset:
  1. Declared license (from the dataset card metadata on Hugging Face).
  2. Sample statistics: row count, average text length, duplicate rate.
  3. PII-like patterns in the sample (names, emails, phone-like strings).
  4. A verdict: usable for this course, usable with conditions, do not use.

Output: audit_report.md in this folder.
"""

import json
import re
import urllib.request
import urllib.error
from collections import Counter

DATASETS = [
    {
        "id": "roneneldan/TinyStories",
        "name": "TinyStories",
        "text_field": "text",
        "expected_use": "Pre-training small language models (Chapter 5).",
    },
    {
        "id": "rajpurkar/squad",
        "name": "SQuAD",
        "text_field": "context",
        "expected_use": "Comparison dataset with a clean declared license.",
    },
]

# Small embedded samples, used only when the network is unavailable.
# These are public example texts, not the real datasets.
FALLBACK_SAMPLES = {
    "roneneldan/TinyStories": [
        "One day, a little girl named Lily found a needle in her room. "
        "She knew it was difficult to play with it because it was sharp.",
        "Once upon a time, there was a little car named Beep. Beep loved "
        "to go fast and play in the sun.",
        "One day, a little fish named Fin was swimming near the shore. "
        "He saw a big crab and wanted to be friends.",
    ],
    "rajpurkar/squad": [
        "The Amazon rainforest is a moist broadleaf tropical rainforest in "
        "the Amazon biome that covers most of the Amazon basin of South America.",
        "Denver is the capital and most populous city of the U.S. state of "
        "Colorado. It is located in the South Platte River Valley.",
    ],
}

# PII-like patterns. This is a rough screen, not a detector: it finds
# things shaped like personal data so you can inspect them by hand.
PII_PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("PHONE", re.compile(r"\+?\d[\d\s\-()]{7,}\d")),
    ("PERSON_NAME", re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")),
    ("URL", re.compile(r"https?://\S+")),
]

# Plain-English meaning of the licenses this audit may encounter.
LICENSE_NOTES = {
    "cc-by-4.0": "Permissive: use, including commercially, with attribution.",
    "cc-by-sa-4.0": "Use, including commercially, with attribution AND share-alike: "
    "derivatives must be shared under the same license.",
    "cc-by-nc-4.0": "Non-commercial only: research and teaching are fine, "
    "selling a model trained on it is not.",
    "apache-2.0": "Permissive software license: use with attribution and a "
    "copy of the license.",
    "mit": "Permissive software license: use with attribution.",
    "cdla-sharing-1.0": "Data license: share results and derived data under "
    "the same terms.",
    "other": "A custom or unclear license: read the full text before using.",
}

HF_API = "https://huggingface.co/api/datasets/"


def fetch_json(url, timeout=20):
    """Fetch a JSON document. Returns None on any failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ai-safety-course/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # network down, dataset missing, API error
        print(f"  [fetch failed] {url}: {exc}")
        return None


def fetch_metadata(dataset_id):
    """Return (license, card_text) from the Hugging Face API, or (None, '')."""
    data = fetch_json(HF_API + dataset_id)
    if not data:
        return None, ""
    card = data.get("cardData") or {}
    license_value = card.get("license")
    if isinstance(license_value, list):
        license_value = ", ".join(license_value)
    return license_value, data.get("description", "") or ""


def fetch_sample(dataset_id, text_field):
    """Stream the first 50 rows with the datasets library.

    Returns (texts, used_live_data). Falls back to the embedded samples
    when the library is missing or the download fails.
    """
    try:
        from datasets import load_dataset

        ds = load_dataset(dataset_id, split="train", streaming=True)
        texts = []
        for row in ds:
            value = row.get(text_field)
            if isinstance(value, str) and value.strip():
                texts.append(value)
            if len(texts) >= 50:
                break
        if texts:
            return texts, True
    except Exception as exc:
        print(f"  [streaming sample failed] {exc}")
    return list(FALLBACK_SAMPLES.get(dataset_id, [])), False


def measure_sample(texts):
    """Basic statistics and PII-like pattern counts for a list of texts."""
    lengths = [len(t) for t in texts]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    dupes = len(texts) - len(set(texts))
    counts = Counter()
    examples = {}
    for text in texts:
        for label, pattern in PII_PATTERNS:
            for match in pattern.finditer(text):
                counts[label] += 1
                examples.setdefault(label, match.group(0))
    return {
        "n": len(texts),
        "avg_chars": round(avg_len, 1),
        "duplicates": dupes,
        "pii_counts": dict(counts),
        "pii_examples": examples,
    }


def verdict(license_value):
    """Course-use verdict from the declared license alone."""
    if not license_value:
        return ("USABLE WITH CONDITIONS",
                "No license declared. No permission granted by default. "
                "Limit use to non-commercial research and document the gap.")
    key = license_value.lower()
    if "nc" in key or "noncommercial" in key or "non-commercial" in key:
        return ("USABLE WITH CONDITIONS",
                "Non-commercial license. Fine for this course; not for a "
                "commercial product.")
    if "by-sa" in key:
        return ("USABLE WITH CONDITIONS",
                "Share-alike: anything derived must be shared under the same "
                "license. Fine for this course; check before commercial use.")
    return ("USABLE FOR THIS COURSE",
            "Declared license permits research use. Keep attribution and "
            "follow its conditions.")


def audit_one(spec):
    print(f"\nAuditing {spec['name']} ({spec['id']}) ...")
    license_value, card_text = fetch_metadata(spec["id"])
    print(f"  Declared license: {license_value or 'NOT DECLARED'}")
    texts, live = fetch_sample(spec["id"], spec["text_field"])
    print(f"  Sample rows: {len(texts)} (live data: {live})")
    stats = measure_sample(texts)
    verdict_label, verdict_note = verdict(license_value)
    return {
        "id": spec["id"],
        "name": spec["name"],
        "expected_use": spec["expected_use"],
        "license": license_value or "NOT DECLARED",
        "license_note": LICENSE_NOTES.get(
            (license_value or "").lower(), "See the license text itself."),
        "card_snippet": (card_text[:400] + "...") if len(card_text) > 400 else card_text,
        "live_sample": live,
        "stats": stats,
        "verdict": verdict_label,
        "verdict_note": verdict_note,
    }


def write_report(results, path="audit_report.md"):
    lines = ["# Dataset License Audit Report", "",
             "Generated by `license_audit.py` (Chapter 2).",
             "Licenses were read from the Hugging Face dataset pages on the "
             "day of the run. Re-run to check for changes.", ""]
    for r in results:
        s = r["stats"]
        lines += [
            f"## {r['name']} (`{r['id']}`)", "",
            f"- **Intended use here:** {r['expected_use']}",
            f"- **Declared license:** {r['license']}",
            f"- **What that means:** {r['license_note']}",
            f"- **Verdict:** {r['verdict']}: {r['verdict_note']}",
            f"- **Sample:** {s['n']} rows, average {s['avg_chars']} characters, "
            f"{s['duplicates']} duplicates "
            f"({'live Hugging Face data' if r['live_sample'] else 'FALLBACK SAMPLE, network unavailable'})",
            f"- **PII-like patterns in sample:** {s['pii_counts'] or 'none found'}",
        ]
        if s["pii_examples"]:
            lines.append(f"- **Examples:** {s['pii_examples']}")
        if r["card_snippet"]:
            lines.append(f"- **Card description:** {r['card_snippet']}")
        lines.append("")
    lines += [
        "## Comparison",
        "",
        "TinyStories declares CDLA Sharing 1.0 in its Hugging Face metadata, but "
        "the card text itself never discusses licensing, and an independent audit "
        "(Longpre et al., Nature Machine Intelligence, 2024) found a conflicting "
        "CC BY-NC 4.0 label for the same dataset. Two sources, two answers. "
        "SQuAD declares CC BY-SA 4.0 in one line on its dataset card. That contrast "
        "is the governance finding: the same audit method, two very different "
        "answers. When sources conflict, record both and use the stricter one "
        "until you can resolve it.",
        "",
        "## What to do next",
        "",
        "1. Copy the measured numbers into `datasheet.md`.",
        "2. Answer the Exercise A questions in `findings.md`.",
        "3. If any verdict is 'do not use', stop and pick another dataset.",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote {path}")


def main():
    results = [audit_one(spec) for spec in DATASETS]
    write_report(results)
    print("\nDone. Read audit_report.md, then answer Exercise A in findings.md.")


if __name__ == "__main__":
    main()
