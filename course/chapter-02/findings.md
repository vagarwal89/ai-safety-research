# Findings: Chapter 2: Training Data Governance

Fill this in as you work. One line per question is enough, but each line must
trace to something you read or ran.

## Exercise A: License audit

Run `python license_audit.py` and paste the measured numbers here.

- TinyStories declared license: cdla-sharing-1.0
- SQuAD declared license: cc-by-sa-4.0
- TinyStories sample: 50  rows, average 693.0 characters, 0 duplicates
- SQuAD sample: 50 rows, average  905.8 characters, 39 duplicates
- PII-like patterns found in TinyStories sample: {'PERSON_NAME': 9}
- PII-like patterns found in SQuAD sample: {'PERSON_NAME': 434, 'PHONE': 5}

1. **TinyStories:** what license, if any, is declared? What does the card say about
   how the stories were generated? Who generated them, and what does that imply
   for your right to use the outputs?
   - Answer: Dataset containing synthetically generated (by GPT-3.5 and GPT-4) short stories that only use a small vocabulary. Described in the following paper: https://arxiv.org/abs/2305.07759. The models referred to in the paper were trained on TinyStories-train.txt (the file tinystories-valid.txt can be used for validation loss). These models can be found on Huggingface, at roneneldan/TinyStories-1M/3M/8M.
2. **SQuAD:** what license is declared? What are the share-alike consequences if
   you fine-tune a model on it and publish the model?
   - Answer: Stanford Question Answering Dataset (SQuAD) is a reading comprehension dataset, consisting of questions posed by crowdworkers on a set of Wikipedia articles, where the answer to every question is a segment of text, or span, from the corresponding reading passage, or the question might be unanswerable. SQuAD 1.1 contains 100,000+
3. **Which dataset has the cleaner governance story, and why?**
   - Answer: TinyStories declares CDLA Sharing 1.0 in its Hugging Face metadata, but the card text itself never discusses licensing, and an independent audit (Longpre et al., Nature Machine Intelligence, 2024) found a conflicting CC BY-NC 4.0 label for the same dataset. Two sources, two answers. SQuAD declares CC BY-SA 4.0 in one line on its dataset card. That contrast is the governance finding: the same audit method, two very different answers. When sources conflict, record both and use the stricter one until you can resolve it.

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
