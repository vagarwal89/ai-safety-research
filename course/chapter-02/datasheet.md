# Datasheet for TinyStories (roneneldan/TinyStories)

A datasheet for datasets, following Gebru et al., "Datasheets for Datasets" (2021).
Fill in the measured values from your run of `license_audit.py` and your reading of
the dataset card. Anything you could not verify stays marked "not verified."

## Motivation

- **Why was the dataset created?** To study how small language models can learn
  fluent English from a small, simple vocabulary. The creators wanted a dataset
  simple enough that a model with only a few million parameters could learn it.
- **Who created it?** Ronen Eldan and Yuanzhi Li (Microsoft Research). Paper:
  "TinyStories: How Small Can Language Models Be and Still Speak Coherent English?"
  (arXiv:2305.07759, 2023).
- **Who funded it?** Not stated on the dataset card. (Mark as not verified.)

## Composition

- **What is in each example?** One short story in plain English, in a single `text`
  field. Stories use a vocabulary of roughly 1,500 words a young child would know.
- **How many examples?** The full release is about 2.2 million stories in the
  original files, plus a GPT-4-only version. The Hugging Face viewer shows the
  `train` split. Record the split size from your audit run: ___
- **Measured sample (from your run):** 50 rows, average 693.0 characters per story,
  0 duplicates in the sample. (Run of November 15, 2026, live Hugging Face data.)
- **What data is missing?** The dataset is synthetic, so there is no real-world
  coverage to measure. Known gap: stories come only from GPT-3.5 and GPT-4
  prompts, so the vocabulary, names, and situations reflect what those models
  produce, not real children's stories.
- **Does it contain personal data?** No real people. Character names (Lily, Tim,
  Sam) are fictional. Your audit found these PII-like patterns in the sample: 9
  PERSON_NAME matches in 50 rows, all false positives on inspection (for example,
  "And Beep" matched the two-capitalized-words pattern). A name in a story is not
  a real person's name, and a scrubber that flags it is over-flagging. Record the
  same lesson for SQuAD: its 39 "duplicates" in 50 rows are the same passage
  repeated across questions, and its 5 "phone numbers" are date ranges like
  2015-2016. A rough screen needs a human to read the matches.
- **Does it contain sensitive or offensive content?** Not by design. The generation
  prompts constrained stories to simple, child-appropriate content. Not verified
  by a full scan: this audit sampled only 50 rows.

## Collection process

- **How was the data acquired?** Generated, not collected. GPT-3.5 and GPT-4
  produced stories from prompts combining a few words (a noun, a verb, an
  adjective) and story features.
- **Over what timeframe?** 2023, before the paper's May 2023 publication.
- **Did the data involve people?** No human subjects. No consent process applies
  to the stories themselves. The underlying models were trained on data that did
  involve people, which is a second-order provenance question: record it here as
  an open item, not as a resolved one.

## Preprocessing and cleaning

- **What was done to the raw data?** Stories were generated with controlled
  prompts and filtered for length and vocabulary. The exact filtering rules are in
  the paper, not on the dataset card.
- **Was any data removed?** Yes: generations that broke the vocabulary or length
  constraints were dropped. Exact counts are not stated on the card.
- **Is the raw data available?** Yes: `tinystories_all_data.tar.gz` and
  `TinyStoriesV2-GPT4-train.txt` are listed on the dataset page.

## Uses

- **What tasks is it for?** Pre-training small language models. This course uses
  it in Chapter 5 (nanoGPT pre-training).
- **What tasks is it NOT for?** Anything needing real-world knowledge, facts, or
  reasoning about the real world. The stories are synthetic and simple by design.
- **What are the license terms?** The Hugging Face metadata declares CDLA Sharing
  1.0 (verified via the API, November 15, 2026). The card text does not discuss
  licensing, and an independent audit found a conflicting CC BY-NC 4.0 label.
  Follow the stricter label: research-only, non-commercial use, and document the
  conflict.

## Distribution

- **Where is it hosted?** Hugging Face, `roneneldan/TinyStories`.
- **Will it be updated?** A GPT-4-only version (TinyStoriesV2) already exists.
  Record the revision you used: ___ (the audit script prints whether it fetched
  live data).

## Maintenance

- **Who maintains it?** The original authors. No maintenance contact is listed
  on the card.
- **How do errors get reported?** Through the Hugging Face dataset discussion
  page. No formal errata exists.

## Article 10(2) mapping (summary)

See `findings.md`, Exercise C, for the full mapping. Headline: collection and
origin (b) and preparation (c) are documented in the paper; bias examination (f),
bias mitigation (g), and data gaps (h) are not documented on the card. Those are
the governance gaps to carry into Chapter 5.
