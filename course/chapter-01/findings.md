# Chapter 1, Exercise A: Systems Inventory Verification

Date: 2026-11-14
File checked: systems_inventory.csv (5 rows)

## Summary

3 rows are correct as filed. 2 rows needed fixes.

- Correct: hiring screening tool, medical triage assistant, movie recommender.
- Fixed: Llama 3 open-weight model, customer-service chatbot.

## Row 1: Llama 3 open-weight model

What the row said as filed: limited-risk.

Verdict: WRONG. This is the biggest error in the file.

Why: the four tiers (unacceptable, high, limited, minimal) classify AI
systems, not models. Llama 3 is a general-purpose AI (GPAI) model, so it
falls under Chapter V of the EU AI Act, not the tier system.

Correct classification: GPAI model, not tiered.
- The 8B and 70B are standard GPAI models. They owe the Art. 53 duties:
  technical documentation, a training-data summary, a copyright policy,
  and information for downstream providers.
- The 405B was trained on about 3.8 x 10^25 FLOPs. That is above the
  10^25 FLOPs threshold in Art. 51(2), so it is presumed a GPAI model
  with systemic risk. It also owes the Art. 55 duties: model evaluation,
  adversarial testing, systemic-risk mitigation, serious-incident
  reporting, and cybersecurity.
- The Art. 53(2) open-source exemption does not save it. The exemption
  only applies to genuinely free and open-source licences, and Meta's
  Llama licence is a custom licence with restrictions. Even if it did
  apply, the exemption is void for a systemic-risk model.

The tier question only becomes real for a system built on Llama 3. A
Llama-powered chatbot is limited-risk (transparency, Art. 50). A
Llama-powered hiring screener is high-risk.

Fix applied to the CSV: tier changed from "limited" to "GPAI, not
tiered: 8B/70B standard GPAI duties; 405B presumed systemic-risk".

## Row 2: Hiring screening tool

What the row said: high-risk, with EU AI Act Arts. 10/13/14/15/17,
GDPR Arts. 9/22/35, Colorado AI Act, DPIA yes.

Verdict: CORRECT.

Why: screening CVs and ranking applicants is recruitment, which is a
high-risk use case under Annex III of the EU AI Act, so the Art. 10
(data governance), 13 (transparency), 14 (human oversight), 15
(accuracy, robustness, cybersecurity), and 17 (quality management)
duties all apply. GDPR Art. 22 applies because it is automated
decision-making about a person. Art. 9 applies because inferred
attributes (for example gender or ethnicity inferred from a name or a
CV) can be special-category data, so the row is right to say
"possibly". Art. 35 DPIA is required. The Colorado AI Act also
applies because employment is a consequential decision under that law.

## Row 3: Customer-service chatbot

What the row said: limited-risk, with GDPR and "EU AI Act transparency
(Art. 52 - user must know it is AI)".

Verdict: MOSTLY CORRECT, one wrong article number.

Why: a support chatbot is limited-risk, and the only AI Act duty is
transparency, telling the user they are talking to an AI. But the
article number is wrong. Transparency is Art. 50 in the final EU AI
Act, not Art. 52. Art. 52 in the old 2021 draft was transparency, and
the number changed in the final law. Art. 52 in the final law is the
procedure for classifying GPAI models, which has nothing to do with
chatbots.

Fix applied to the CSV: "Art. 52" changed to "Art. 50".

DPIA note: the row says "yes - if large-scale profiling". That is
right as a conditional. A plain chatbot answering support questions
does not need a DPIA. It would need one only if it started profiling
customers at large scale.

## Row 4: Medical triage assistant

What the row said: high-risk, health data as special-category data,
GDPR Arts. 9/35, EU AI Act high-risk, HIPAA if US health data, DPIA yes.

Verdict: CORRECT.

Why: prioritising patients by symptoms is a medical use case, which is
high-risk under Annex III, and health data is special-category data
under GDPR Art. 9, so a DPIA under Art. 35 is required. HIPAA applies
only if US health data is involved, which the row states correctly as
a conditional.

## Row 5: Movie recommender

What the row said: minimal-risk, GDPR minimisation and purpose
limitation, DPIA no.

Verdict: CORRECT.

Why: suggesting films from watch history is not a high-risk use case,
does not trigger a transparency duty, and does not process
special-category data. The GDPR duties that do apply are the basics:
collect only what is needed (minimisation) and use it only for the
purpose stated (purpose limitation). No DPIA is needed.

## Corrections made to systems_inventory.csv

1. Llama 3 row: tier "limited" changed to "GPAI, not tiered: 8B/70B
   standard GPAI duties; 405B presumed systemic-risk".
2. Chatbot row: "Art. 52" changed to "Art. 50".

## Lesson learned

Article numbers are not portable between laws. GDPR Art. 10, 13, 15,
and 17 mean different things from EU AI Act Art. 10, 13, 15, and 17.
Always write the law name before the article number.

## Exercise B: PII scan (Presidio)

Ran pii_scan.py on the five sample texts. Presidio reported 18 entities.

### 1. What did it find, by type?

| Entity type    | Count |
| -------------- | ----- |
| DATE_TIME      | 5     |
| LOCATION       | 5     |
| PERSON         | 3     |
| PHONE_NUMBER   | 2     |
| URL            | 2     |
| EMAIL_ADDRESS  | 1     |
| TOTAL          | 18    |

Most common: DATE_TIME and LOCATION, tied at 5 each.

But 18 is not the real score. Four of the 18 are false positives, and
one is the right text with the wrong label:

- Sample 1: "example.com" and a fragment of the email address were
  flagged as URL. They are parts of the email that was already
  detected, not separate entities.
- Sample 2: the ZIP code "98031" was flagged as DATE_TIME.
- Sample 4: the confirmation code "AB-8842-KL" was flagged as
  DATE_TIME.
- Sample 5: "45-year-old" was flagged as DATE_TIME. The age was
  detected, but as the wrong type.

So the honest count is 13 clean hits out of 18 detections, 4 false
positives, 1 misclassified. Detection is never perfect in either
direction: it misses real identifiers and invents fake ones.

### 2. What did it miss?

Sample 5, item by item:

- Nickname "Viv": MISSED. Not flagged as PERSON. Presidio only
  recognises full names it has seen in training data. A nickname at
  the start of a sentence looks like an ordinary word to it.
- Indian phone "+91 98765 43210": CAUGHT. Presidio did get this one,
  so the Indian format is not the problem. The exercise predicted a
  miss here and the prediction was wrong. Record that.
- Indirect identifier "the 45-year-old manager from Kent": MISSED as
  an identifier. "45-year-old" was flagged as DATE_TIME, which is the
  wrong type, and "manager" plus the combination were not flagged at
  all. Age plus job plus city is a quasi-identifier: on its own each
  piece is harmless, together they narrow a person down fast.
- UPI id "viv.k@okhdfcbank": MISSED entirely. No entity fired. It
  looks like an email address, but it has no dot in the domain, so
  Presidio's email pattern does not match it.

Misses in the other samples:

- Sample 2: the house number "20123" in "20123 98th Avenue South".
  Presidio caught the street and city as LOCATION but not the number,
  so the address survives in pieces.
- Sample 3: the employee ID "EMP-48210". No recogniser exists for it
  by default.
- Sample 4: the card ending "9317". Presidio's credit-card recogniser
  needs a full valid card number, so a partial number slips through.
  The confirmation code "AB-8842-KL" was detected but as DATE_TIME,
  the wrong type, so it would also survive a scrub that only removes
  detected identifiers.

### 3. Why does the miss matter for a training-data pipeline?

A scrubber that misses indirect identifiers gives a false sense of
safety. After scrubbing, sample 5 looks clean: no name, no email, no
address. But "Viv, the 45-year-old manager from Kent, UPI id
viv.k@okhdfcbank" still identifies one person. Anyone who knows the
team can pick him out from age plus role plus city, and the UPI id is
a direct handle to his bank account.

That gap between "looks clean" and "is clean" is the whole privacy
story of the next chapters. If this text went into a training set:

- The PII is now in the training data, which breaks GDPR
  minimisation (Art. 5(1)(c)) and the EU AI Act data-governance duty
  (Art. 10), because the data was supposed to be cleaned before
  training.
- The model can memorise it. Chapter 6 shows how extraction attacks
  pull memorised names, numbers, and identifiers back out of a
  trained model. A miss at the scrubbing stage becomes a leak at the
  model stage.
- The false positives cause damage in the other direction. Scrubbing
  a ZIP code and a confirmation code because they look like dates
  corrupts the data, and a model trained on corrupted data learns the
  wrong patterns.

Measurement lesson: the misses are the finding. A detector that
reports "18 entities found" sounds thorough. Counting what it missed
and what it invented is what tells you whether the pipeline is safe.

