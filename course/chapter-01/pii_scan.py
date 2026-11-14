"""Chapter 1 - your first PII scan.

Run:  python pii_scan.py

Needs: pip install presidio-analyzer presidio-anonymizer
       python -m spacy download en_core_web_sm

If Presidio is not installed, the script falls back to simple regexes
so you can still run the exercise and see the idea (and the misses).
The fallback is deliberately weaker than Presidio - that gap IS the lesson.
"""

import re
from collections import Counter

SAMPLE_TEXTS = [
    # 1. Straightforward: name, email, phone, date.
    "Hi, I'm Priya Sharma. You can reach me at priya.sharma@example.com "
    "or on 650-555-0142. My appointment is on March 3, 2026.",
    # 2. Address and location.
    "Please send the documents to Arjun Mehta, 20123 98th Avenue South, "
    "Kent, WA 98031, United States.",
    # 3. Work context: name, employer, ID-like number.
    "Employee Rahul Verma (ID EMP-48210) from the Bangalore office "
    "submitted his leave request on 12/01/2026.",
    # 4. Money and account-ish numbers.
    "Your order total is $184.20. Card ending 9317 was charged. "
    "Confirmation code: AB-8842-KL.",
    # 5. The tricky one: nickname, indirect identifier, non-US phone format.
    "Viv, the 45-year-old manager from Kent, can be reached on "
    "+91 98765 43210 or at his UPI id viv.k@okhdfcbank.",
]

# --- Fallback: plain regexes, used only if Presidio is unavailable. ---
REGEX_PATTERNS = [
    ("EMAIL_ADDRESS", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("PHONE_NUMBER", re.compile(r"\+?\d[\d\s\-()]{7,}\d")),
    ("PERSON", re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")),
    ("LOCATION", re.compile(r"\b(?:Kent|Bangalore|Washington)\b")),
    ("DATE_TIME", re.compile(r"\b(?:\d{1,2}/\d{1,2}/\d{4}|March \d{1,2}, \d{4})\b")),
]


def scan_with_presidio(texts):
    from presidio_analyzer import AnalyzerEngine

    analyzer = AnalyzerEngine()
    all_results = []
    for text in texts:
        results = analyzer.analyze(text=text, language="en")
        found = [(r.entity_type, text[r.start:r.end]) for r in results]
        all_results.append(found)
    return all_results, "presidio"


def scan_with_regex(texts):
    all_results = []
    for text in texts:
        found = []
        for entity_type, pattern in REGEX_PATTERNS:
            for match in pattern.finditer(text):
                found.append((entity_type, match.group(0)))
        all_results.append(found)
    return all_results, "regex-fallback"


def main():
    try:
        results, engine = scan_with_presidio(SAMPLE_TEXTS)
    except Exception as exc:  # Presidio missing or model not downloaded
        print(f"Presidio unavailable ({exc}); using regex fallback.\n")
        results, engine = scan_with_regex(SAMPLE_TEXTS)

    print(f"Engine: {engine}\n")
    counts = Counter()
    for i, (text, found) in enumerate(zip(SAMPLE_TEXTS, results), start=1):
        print(f"--- Sample {i} ---")
        print(f"Text: {text}")
        if not found:
            print("Found: nothing")
        for entity_type, value in sorted(found):
            print(f"  {entity_type:15s} {value}")
            counts[entity_type] += 1
        print()

    print("=== Totals by entity type ===")
    for entity_type, n in counts.most_common():
        print(f"  {entity_type:15s} {n}")
    print(f"  {'TOTAL':15s} {sum(counts.values())}")
    print()
    print("Now answer in findings.md:")
    print("  1. What did it find, by type?")
    print("  2. What did it MISS in sample 5 (nickname? indirect identifier?")
    print("     Indian phone format? UPI id?)")
    print("  3. Why does the miss matter for a training-data pipeline?")


if __name__ == "__main__":
    main()
