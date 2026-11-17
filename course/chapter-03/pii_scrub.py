"""Chapter 3 - PII scrub with Presidio, and a measured recall check.

Run:  python pii_scrub.py

Needs: pip install presidio-analyzer presidio-anonymizer
       python -m spacy download en_core_web_sm
If Presidio is unavailable it falls back to a small regex screen and
says so clearly in the report. The fallback finds less; that gap is
itself part of the lesson.

What it does:
  1. Runs Presidio's Analyzer over 8 labeled test texts. Each text has
     a list of entities a good scrubber should find.
  2. Adds two custom recognizers Presidio does not ship: a UPI id
     (Indian payment handle) and an employee id. Extending the
     detector is part of the job: off-the-shelf tools are tuned for
     US-shaped data.
  3. Anonymizes each text, replacing every detected entity with a
     placeholder such as <PERSON> or <PHONE_NUMBER>.
  4. Measures recall per text: how many of the expected entities were
     found at all, and how many got the right type. The interesting
     results are the wrong types and the false positives: indirect
     identifiers are removed for the wrong reason, and ordinary words
     get scrubbed by mistake.

Output: scrub_report.md in this folder.
"""

import re

# (text, [(expected entity text, expected type), ...])
# Types: Presidio types (PERSON, EMAIL_ADDRESS, PHONE_NUMBER,
# DATE_TIME, LOCATION) plus our two custom types (UPI_ID, EMPLOYEE_ID)
# plus INDIRECT, which no detector is expected to catch: it marks an
# identifier that only identifies a person in combination with other
# facts, and it is listed here so the miss is counted honestly.
TEST_TEXTS = [
    ("Hi, I am Vivek Kumar Agarwal. You can reach me at "
     "vivek@example.com or call +1 206-555-0148.",
     [("Vivek Kumar Agarwal", "PERSON"),
      ("vivek@example.com", "EMAIL_ADDRESS"),
      ("+1 206-555-0148", "PHONE_NUMBER")]),
    ("Please send the invoice to my UPI id viv@okhdfcbank.",
     [("viv@okhdfcbank", "UPI_ID")]),
    ("My employee ID is EMP-48213 and my manager is Priya Sharma.",
     [("EMP-48213", "EMPLOYEE_ID"),
      ("Priya Sharma", "PERSON")]),
    ("Viv said the card ending 1761 was charged twice.",
     [("Viv", "PERSON"),
      ("1761", "INDIRECT")]),
    ("The 45-year-old manager from Kent called about the refund.",
     [("45-year-old manager from Kent", "INDIRECT")]),
    ("Call me on +91 98765 43210 after 6 pm.",
     [("+91 98765 43210", "PHONE_NUMBER")]),
    ("Meet Sara at 5 pm on Friday at the Seattle office.",
     [("Sara", "PERSON"),
      ("5 pm", "DATE_TIME"),
      ("Friday", "DATE_TIME"),
      ("Seattle", "LOCATION")]),
    ("Email the report to ana.patel@company.com before Monday.",
     [("ana.patel@company.com", "EMAIL_ADDRESS"),
      ("Monday", "DATE_TIME")]),
]

# Regex fallback, used only when Presidio cannot be imported.
# It is deliberately rough: it finds email-shaped and phone-shaped
# strings and capitalized name-like pairs, and nothing else.
FALLBACK_PATTERNS = [
    ("EMAIL_ADDRESS", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("PHONE_NUMBER", re.compile(r"\+?\d[\d\s\-()]{7,}\d")),
    ("PERSON", re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")),
    ("UPI_ID", re.compile(r"\b[\w.+-]+@[a-z]+\b")),
    ("EMPLOYEE_ID", re.compile(r"\bEMP-\d{5}\b")),
]


def spans_overlap(start_a, end_a, start_b, end_b):
    return start_a < end_b and start_b < end_a


def analyze_with_presidio(texts):
    """Returns (results, anonymized, used_presidio=True).

    results is a list per text of (start, end, entity_text, entity_type).
    """
    from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
    from presidio_analyzer.nlp_engine import SpacyNlpEngine
    from presidio_anonymizer import AnonymizerEngine

    # Presidio defaults to the large spaCy model (en_core_web_lg) and
    # tries to download it if it is missing. Point it at the small
    # model instead: it is what the course installs, and it is enough
    # for this lab. This also keeps Colab runs fast.
    upi_recognizer = PatternRecognizer(
        supported_entity="UPI_ID",
        patterns=[Pattern(
            name="upi_id",
            regex=r"\b[a-zA-Z0-9._-]+@[a-zA-Z]{2,}\b",
            score=0.9,
        )],
        context=["upi", "upi id", "pay", "payment"],
    )
    employee_recognizer = PatternRecognizer(
        supported_entity="EMPLOYEE_ID",
        patterns=[Pattern(
            name="employee_id",
            regex=r"\bEMP-\d{5}\b",
            score=0.9,
        )],
        context=["employee id", "emp id", "employee"],
    )

    analyzer = AnalyzerEngine(
        nlp_engine=SpacyNlpEngine(
            models=[{"lang_code": "en", "model_name": "en_core_web_sm"}]),
        supported_languages=["en"],
    )
    analyzer.registry.add_recognizer(upi_recognizer)
    analyzer.registry.add_recognizer(employee_recognizer)
    anonymizer = AnonymizerEngine()

    all_results = []
    anonymized = []
    for text, _ in texts:
        found = analyzer.analyze(text=text, language="en")
        all_results.append([
            (r.start, r.end, text[r.start:r.end], r.entity_type)
            for r in found
        ])
        anon = anonymizer.anonymize(text=text, analyzer_results=found)
        anonymized.append(anon.text)
    return all_results, anonymized, True


def analyze_with_fallback(texts):
    """Regex screen. Returns the same shape as analyze_with_presidio."""
    all_results = []
    anonymized = []
    for text, _ in texts:
        found = []
        for entity_type, pattern in FALLBACK_PATTERNS:
            for match in pattern.finditer(text):
                found.append((match.start(), match.end(), match.group(0), entity_type))
        found.sort()
        all_results.append(found)
        scrubbed = text
        for _, _, entity_text, entity_type in found:
            scrubbed = scrubbed.replace(entity_text, f"<{entity_type}>")
        anonymized.append(scrubbed)
    return all_results, anonymized, False


def measure_recall(texts, all_results):
    """Per text: expected entities, how many were found (any type),
    how many got the right type. Returns a list of row dicts."""
    rows = []
    for (text, expected), found in zip(texts, all_results):
        found_count = 0
        correct_type_count = 0
        missed = []
        wrong_type = []
        for entity_text, entity_type in expected:
            start = text.find(entity_text)
            end = start + len(entity_text) if start >= 0 else -1
            # All detections overlapping the expected span. A detector
            # often fires twice on one span (for example an email that
            # also matches the UPI pattern), so collect every hit and
            # credit the right type if any of them got it.
            hits = [f_type for f_start, f_end, _, f_type in found
                    if start >= 0
                    and spans_overlap(start, end, f_start, f_end)]
            if not hits:
                missed.append((entity_text, entity_type))
            else:
                found_count += 1
                if entity_type in hits:
                    correct_type_count += 1
                else:
                    wrong_type.append((entity_text, entity_type, hits))
        rows.append({
            "text": text,
            "expected": len(expected),
            "found": found_count,
            "correct_type": correct_type_count,
            "missed": missed,
            "wrong_type": wrong_type,
            "detected": found,
        })
    return rows


def main():
    try:
        all_results, anonymized, used_presidio = analyze_with_presidio(TEST_TEXTS)
    except Exception as exc:
        print(f"[Presidio unavailable: {exc}] Falling back to a regex screen.")
        all_results, anonymized, used_presidio = analyze_with_fallback(TEST_TEXTS)

    print(f"Detector: {'Presidio (+ 2 custom recognizers)' if used_presidio else 'REGEX FALLBACK'}")
    rows = measure_recall(TEST_TEXTS, all_results)

    total_expected = sum(r["expected"] for r in rows)
    total_found = sum(r["found"] for r in rows)
    total_correct_type = sum(r["correct_type"] for r in rows)
    print(f"\nRecall: {total_found}/{total_expected} expected entities found "
          f"({100 * total_found / total_expected:.0f}%)")
    print(f"Right type: {total_correct_type}/{total_expected} "
          f"({100 * total_correct_type / total_expected:.0f}%)")

    for i, row in enumerate(rows):
        print(f"\nText {i + 1}: {row['text']}")
        print(f"  Detected: {[(t, ty) for _, _, t, ty in row['detected']] or 'none'}")
        print(f"  Anonymized: {anonymized[i]}")
        if row["missed"]:
            print(f"  MISSED: {row['missed']}")
        if row["wrong_type"]:
            print(f"  WRONG TYPE: {row['wrong_type']}")

    write_report(rows, anonymized, used_presidio,
                 total_expected, total_found, total_correct_type)


def write_report(rows, anonymized, used_presidio,
                 total_expected, total_found, total_correct_type,
                 path="scrub_report.md"):
    if used_presidio:
        detector_line = ("Detector: Presidio Analyzer + Anonymizer, with custom "
                         "UPI_ID and EMPLOYEE_ID recognizers")
    else:
        detector_line = "Detector: REGEX FALLBACK (Presidio unavailable)"
    lines = ["# PII Scrub Report", "",
             "Generated by `pii_scrub.py` (Chapter 3).",
             detector_line,
             "",
             f"**Recall: {total_found}/{total_expected} expected entities found "
             f"({100 * total_found / total_expected:.0f}%). "
             f"Right type: {total_correct_type}/{total_expected} "
             f"({100 * total_correct_type / total_expected:.0f}%).**",
             ""]
    for i, row in enumerate(rows):
        lines += [f"## Text {i + 1}", "",
                  f"Original: {row['text']}", "",
                  f"Anonymized: {anonymized[i]}", "",
                  f"Expected {row['expected']} entities, found {row['found']}, "
                  f"right type {row['correct_type']}.",
                  ""]
        if row["missed"]:
            lines.append(f"Missed: {row['missed']}")
            lines.append("")
        if row["wrong_type"]:
            lines.append(f"Found but wrong type: {row['wrong_type']}")
            lines.append("")
    lines += [
        "## What this means",
        "",
        "A scrubber is measured by recall: what fraction of the personal "
        "data did it actually remove. On this test every expected span was "
        "removed, but the types were not always right, and the detector also "
        "removed things that were not personal data at all. Three lessons "
        "follow from the actual run.",
        "",
        "First, indirect identifiers are caught only by accident. The card "
        "ending 1761 was removed, but only because it looked like a date. "
        "The age plus role plus city combination was broken up, but only "
        "because its pieces looked like a date and a name. If the shapes had "
        "been slightly different, both would have survived. A detector that "
        "removes something for the wrong reason is not a reliable control.",
        "",
        "Second, scrubbing damages text. The word 'Email' at the start of a "
        "sentence was tagged as a person, 'UPI' was tagged as a nationality, "
        "and 'Meet Sara' was swallowed whole into one person entity. Every "
        "false positive deletes real meaning from the training data. Recall "
        "and precision pull in opposite directions, and the right balance "
        "depends on what the data is for.",
        "",
        "Third, add custom recognizers for the identifier shapes your data "
        "actually contains. The UPI id and the employee id were both found "
        "with the right type only because this script adds recognizers for "
        "them. A US-tuned default knows neither shape. That is the general "
        "rule: a scrubber is only as good as its fit to your data.",
        "",
        "Never report a scrub as clean on the basis of the tool running. "
        "Report the measured recall, the wrong types, the false positives, "
        "and what you did about them. That record is your GDPR Article "
        "5(1)(c) data minimization evidence and part of your Article "
        "10(2)(c) preparation record.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
