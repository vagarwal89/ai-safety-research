# Findings: Chapter 2: Training Data Governance

Fill this in as you work. One line per question is enough, but each line must
trace to something you read or ran.

## Exercise A: License audit

Run `python license_audit.py` and paste the measured numbers here.

- TinyStories declared license: ___
- SQuAD declared license: ___
- TinyStories sample: ___ rows, average ___ characters, ___ duplicates
- SQuAD sample: ___ rows, average ___ characters, ___ duplicates
- PII-like patterns found in TinyStories sample: ___
- PII-like patterns found in SQuAD sample: ___

1. **TinyStories:** what license, if any, is declared? What does the card say about
   how the stories were generated? Who generated them, and what does that imply
   for your right to use the outputs?
   - Answer: ___
2. **SQuAD:** what license is declared? What are the share-alike consequences if
   you fine-tune a model on it and publish the model?
   - Answer: ___
3. **Which dataset has the cleaner governance story, and why?**
   - Answer: ___

## Exercise B: Purpose-limitation test

### Customer-service chatbot (support chat logs)

1. Original purpose (one sentence): ___
2. Training purpose (one sentence): ___
3. Article 6(4) factors:
   - Link between the purposes: ___
   - Context of collection: ___
   - Nature of the data: ___
   - Consequences for the person: ___
   - Safeguards you would apply: ___
4. Verdict (compatible / compatible with safeguards / not compatible): ___

### TinyStories (Chapter 5 training)

1. Original purpose (one sentence): ___
2. Training purpose (one sentence): ___
3. Verdict: ___ (reasoning: ___)

## Exercise C: Article 10(2) mapping for TinyStories

One line of evidence, or one line admitting a gap, for each practice.

- (a) design choices: ___
- (b) collection and origin: ___
- (c) preparation operations: ___
- (d) assumptions: ___
- (e) availability and suitability: ___
- (f) bias examination: ___
- (g) bias mitigation: ___
- (h) gaps and shortcomings: ___

## What I would do differently next time

- ___
