# Datasheet for the Chapter 7 SFT dataset (sft_data.jsonl)

A datasheet for datasets, following Gebru et al., "Datasheets for
Datasets" (2021). SFT data is training data, so it gets the same
treatment as the pre-training data in Chapter 2: origin, composition,
cleaning, and limits, all written down before training starts.

## Motivation

- **Why was the dataset created?** To teach a base model to answer
  governance, privacy, and AI safety questions in the style of a short,
  accurate assistant reply. It is a teaching dataset for one lab, not
  a production dataset.
- **Who created it?** Vivek Kumar Agarwal, for this course, November
  20, 2026. Every completion was written by hand for this chapter.
- **Who funded it?** No funding. Personal study.

## Composition

- **What is in each example?** One JSON object with a `prompt`
  (the instruction) and a `completion` (the desired response).
  Prompts cover definitions, how-to questions, and concept
  comparisons in data protection, third-party risk, and AI safety.
- **How many examples?** 40 training examples, plus 10 held-out test
  prompts in test_prompts.jsonl. Measured November 20, 2026:
  average prompt 6.2 words, average completion 41.7 words.
- **What data is missing?** This dataset teaches format and a narrow
  set of concepts, not knowledge. 40 examples cannot teach a model
  new facts. Anything the model does not already know from
  pre-training, it will still not know after this SFT run.
- **Does it contain personal data?** No. Checked November 20, 2026
  with dataset_checks.py: 0 email, phone, long digit run, or URL
  patterns in any prompt or completion. All names, companies, and
  situations are generic or fictional. No real person is named.
- **Is it representative?** No. It covers one person's teaching
  priorities for one lab. It is not a sample of real user questions.

## Collection

- **How was the data collected?** Written by hand, one example at a
  time, from the course material in Chapters 1 to 6 and from the
  regulation hooks those chapters established.
- **What was the labeling process?** The completion IS the label: each
  prompt was paired with the response a careful assistant should
  give. There was no crowd labeling and no scraped user data.
- **Did any person provide data about themselves?** No.

## Preprocessing

- **What cleaning was done?** Three gates, in pipeline order.
  1. Dedup (Chapter 3 method): dataset_checks.py found 0 exact
     duplicate prompts and 0 near-duplicates at Jaccard 0.8 or
     above.
  2. PII pre-check (Chapter 3 method): 0 PII-shaped patterns.
     The Presidio scrub from Chapter 3 should also be run on this
     file; record the result in findings.md.
  3. Contamination check: 4 of the first 10 test prompts were
     verbatim copies of training prompts. They were rewritten as
     paraphrases on new angles, and the re-check found 0 overlaps
     at Jaccard 0.8 or above. The first version of the test set was
     not a test, and the check caught it.
- **Was any data removed?** No examples were removed. 4 test prompts
  were rewritten, not deleted.

## Uses

- **What is it for?** One QLoRA SFT run on TinyLlama-1.1B, and the
  base vs SFT comparison in this chapter.
- **What must it NOT be used for?** It must not be used as evidence
  that the SFT model knows the law, or as training data for a real
  assistant that answers real users. 40 examples teach the shape of
  an answer, not the substance of one.
- **Can it be shared?** Yes. It contains no personal data and no
  third-party text. License: CC0 (public domain dedication), so it
  can be reused without restriction.

## Maintenance

- **Who maintains it?** The course author, for the duration of the
  course.
- **Will it be updated?** Only to fix errors found during the lab.
  Any fix changes the file and the datasheet together, with a dated
  note in findings.md.
