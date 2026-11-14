# Chapter 1 — One System: Regulation, Privacy, and AI Safety

**Time:** ~60–90 minutes. **Needs:** a browser (Google Colab), nothing installed locally.
**You will finish with:** a system inventory, your first PII scan, and a lab setup that carries all 15 chapters.

---

## 1. The one picture

Forget three separate subjects. There is one pipeline, and everything in this course hangs on it:

```
DATA  →  MODEL  →  DEPLOYMENT  →  PEOPLE
```

- **Data:** where the model learns from. Privacy lives here first.
- **Model:** what the model can do, and what it memorized. Safety evals live here.
- **Deployment:** who uses it, how it is monitored, what happens when it fails. Governance lives here.
- **People:** who is harmed or helped. Every regulation is ultimately about this end.

Every rule you will meet attaches to a stage of this pipeline. When you are confused by a
regulation, ask: *which stage does it govern, and what harm is it trying to prevent?*

## 2. The three regimes, in plain English

### GDPR (EU privacy law) — governs the DATA stage, and the person behind it
- **Art. 5 — the seven principles:** lawfulness, purpose limitation, data minimization,
  accuracy, storage limitation, integrity/confidentiality, accountability. If you remember
  one article, remember this one.
- **Art. 9 — special-category data:** race, health, biometrics, political opinions, and
  more. Processing it is banned by default, with narrow exceptions. This is the article
  that collides with fairness testing in Chapter 12.
- **Art. 35 — DPIA:** a Data Protection Impact Assessment is required before high-risk
  processing. Your system inventory (Exercise A) is the first half of a DPIA.
- **Art. 22 — automated decisions:** people have rights when a machine decides about them.

Key idea: GDPR protects the *person*, not the model. The question is always "what happens
to the individual whose data this is?"

### EU AI Act — governs the MODEL and DEPLOYMENT stages, by risk
- **Risk tiers:** unacceptable (banned), high-risk, limited-risk (transparency duties),
  minimal-risk (mostly free).
- **High-risk duties:** Art. 10 data governance, Art. 13 transparency, Art. 14 human
  oversight, Art. 15 accuracy, robustness and cybersecurity, Art. 17 quality management.
- **Timing:** general-purpose AI duties since August 2025; high-risk duties phase in
  through 2026–2027. This is live law, not a proposal.

Key idea: the Act does not ask "is AI good or bad?" It asks "how risky is this use, and
what controls match that risk?" That is the same question you will ask in every lab.

### US law — a patchwork, with one framework everyone speaks
- **Colorado AI Act:** high-risk AI systems need impact assessments and disclosures.
- **California SB 53:** frontier-model transparency and reporting, effective January 1, 2026.
- **NIST AI RMF:** voluntary, but it is the shared language of the field — Govern, Map,
  Measure, Manage. It is the spine of this course (see section 3).

Key idea: US law is fragmented, so practitioners anchor on NIST AI RMF and on the EU
rules, because global products have to satisfy the strictest regime anyway.

## 3. Your spine: Govern-wrapped Map, Measure, Manage

This is the loop you will use in every chapter, and in interviews:

> **Map** discovers and classifies. **Measure** tests and monitors. **Manage** controls
> and remediates. **Govern** holds the owners, the rationale, and the evidence.

- Chapter 1 maps: the inventory.
- Chapters 3–6 measure: dedup rates, PII recall, memorization.
- Chapters 7–13 manage: controls like DP, DPO, defenses, release gates.
- Chapter 14 proves: the safety case is the evidence Govern holds.

Say it in one line: *"I run a Govern-wrapped Map, Measure, Manage loop. Map discovers and
classifies, Measure tests and monitors, Manage controls and remediates, and Govern holds
the owners, the rationale, and the evidence."*

## 4. Lab setup — do this now (15 minutes)

You do not need a powerful computer. You will use **Google Colab** (free, runs in the browser,
gives you a GPU when you need one) and **GitHub** (where your work lives).

1. Open https://colab.research.google.com and sign in with your Google account.
2. Click File → New notebook. Run this in the first cell to check your Python:
   ```python
   import sys
   print(sys.version)  # want 3.10 or newer
   ```
3. In a new cell, install the one tool this chapter needs:
   ```python
   !pip install -q presidio-analyzer presidio-anonymizer
   !python -m spacy download en_core_web_sm
   ```
   (Presidio is Microsoft's open-source PII detection library. It is the standard tool for
   the "find personal data in text" job, and you will reuse it in Chapters 2, 3, 6, and 9.)
4. Clone your course repo so your work has a home (on your own computer, or in Colab):
   ```bash
   git clone https://github.com/vagarwal89/ai-safety-research.git
   cd ai-safety-research/course/chapter-01
   ```

If the Presidio install fails, do not stop: the script in this folder has a regex fallback
so you can still run the exercise and see the idea. Fix the install later.

## 5. Exercise A — Build a system inventory (20 minutes)

Open `systems_inventory.csv` in this folder. It lists five AI systems with these columns:

| Column | What to put in it |
|---|---|
| system | name of the system |
| use_case | what it does, in one line |
| eu_ai_act_tier | unacceptable / high / limited / minimal |
| personal_data | what personal data it touches |
| special_category_data | yes/no — does it touch Art. 9 data? |
| regulation_triggered | GDPR, EU AI Act Art. __, Colorado AI Act, SB 53… |
| dpia_needed | yes/no — would Art. 35 require an impact assessment? |

Five systems are pre-filled as examples. Your job: **verify each row and fix what is wrong.**
For each one, ask: is the tier right? (A hiring-screening tool is high-risk under the AI Act.
A movie recommender is minimal-risk.) Does it touch special-category data? Would a DPIA be
required? Write your reasoning in `findings.md` — one line per system.

This inventory is the Map phase. It is also the first half of a real DPIA, and it is the
artifact a regulator or an auditor asks for first.

## 6. Exercise B — Your first PII scan (20 minutes)

Run the script:

```bash
python pii_scan.py
```

It scans five short sample texts with Presidio and prints every entity it finds: names,
emails, phone numbers, locations, dates. Then answer these three questions in `findings.md`:

1. **What did it find?** Count entities by type. Which type appears most?
2. **What did it miss?** Look at sample 5. It contains a nickname, an indirect identifier
   ("the 45-year-old manager from Kent"), and an Indian phone number format. Presidio will
   miss some of these. Write down exactly which ones.
3. **Why does the miss matter?** A PII scrubber that misses indirect identifiers gives a
   false sense of safety: the data looks clean, but a person is still identifiable. That gap
   between "looks clean" and "is clean" is the privacy story of Chapters 2, 3, and 6.

This is your first measurement. Detection is never perfect, and the misses are the finding.

## 7. What to push to GitHub

In `course/chapter-01/`:
- `README.md` — this file.
- `pii_scan.py` — the scan script (already here; run it).
- `systems_inventory.csv` — your verified inventory.
- `findings.md` — your answers: one line per system, plus the three PII questions.

## 8. Check yourself

1. Name one rule that attaches at the data stage, one at the model stage, one at deployment.
2. Why does EU AI Act Art. 10(5) exist? (Hint: it is the answer to the Art. 10 vs Art. 9 collision.)
3. What did Presidio miss in your sample, and why does that matter for a training-data pipeline?

## 9. Paper seed

Your inventory plus your scan results are the seed of a DPIA-style case study: "What a
standard PII scrubber misses in realistic text, and what that means for AI Act Art. 10
compliance." Keep every finding. Chapter 15 turns your best lab into a paper.

## Key terms (first-use glossary)

- **PII:** personally identifiable information — any data that can identify a person.
- **DPIA:** Data Protection Impact Assessment (GDPR Art. 35).
- **Special-category data:** GDPR Art. 9 data (health, race, biometrics, etc.) — banned by default.
- **High-risk AI system:** EU AI Act category with the heaviest duties (Art. 10, 13, 14, 15, 17).
- **Presidio:** Microsoft's open-source PII detection and anonymization library.
- **NIST AI RMF:** the US framework: Govern, Map, Measure, Manage.
