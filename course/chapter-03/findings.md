# Findings: Chapter 3: Data Prep That Holds Up

Fill this in as you work. One line per question is enough, but each line must
trace to something you read or ran. The measured numbers from the November 16,
2026 run are already filled in below; your job is the reasoning.

## Measured results (November 16, 2026 run)

- Dedup, live TinyStories sample: 60 stories, 0 pairs above the 0.7 threshold.
  Most similar pair: stories 31 and 43, estimated Jaccard 0.094, exact 0.028.
  Dedup pass removed 0 of 60 stories.
- Dedup, fallback sample (planted duplicates): identical pair 1.0, one-word-change
  pair 0.844 estimated / 0.773 exact, different-ending pair below threshold.
  Dedup pass kept 12 of 14 stories, removed 2.
- PII scrub: recall 16/16 expected spans removed (100%), right type 14/16 (88%).
  Wrong types: card ending 1761 labeled DATE_TIME; age plus role plus city
  labeled DATE_TIME / PERSON. False positives: "Email" as PERSON, "UPI" as NRP,
  "Meet Sara" swallowed into one PERSON entity.
- BPE tokenizer: 100 merges on 100 stories (14,929 words, 1,431 unique words).
  Vocabulary 127 tokens. Test sentences: 48 tokens for 21 words, 2.29 tokens
  per word. All three round trips exact. Unseen word "xylophone" fell back to
  single letters and small pieces.

## Exercise A: MinHash near-dedup

1. **Live sample:** how many near-duplicate pairs, and what was the most similar
   pair? What does a zero result mean: clean data, or a threshold too strict
   for short stories?
   - Answer: ___
2. **Fallback sample:** is keeping the different-ending pair the right call?
   Would you remove it or keep it, and why?
   - Answer: ___
3. **Threshold:** after re-running with THRESHOLD 0.5 and 0.9, what appeared and
   what disappeared? What threshold would you pick for the full 2.1 million
   TinyStories, and why?
   - Threshold I would pick: ___
   - Reasoning: ___
4. **Scale:** why does MinHash plus LSH banding fix the pairwise comparison
   problem? What does banding let you skip, and what does it cost?
   - Answer: ___

## Exercise B: PII scrub

1. **Recall:** name the two wrong types. For each, was the personal data still
   removed, and would you trust the scrubber on the same shape next time?
   - Answer: ___
2. **False positives:** pick one ("Email" as PERSON, "UPI" as NRP, or "Meet
   Sara") and explain what it does to training data at scale. What would you
   change to reduce it?
   - Answer: ___
3. **Add a recognizer:** which identifier shape did you add, what pattern did
   you use, and did it fire correctly?
   - Shape: ___
   - Pattern: ___
   - Result: ___
4. **My scrub standard for this course:** what recall do I require, how will I
   measure it, and what do I do when the measurement falls short?
   - Answer: ___

## Exercise C: BPE tokenizer

1. **Merges:** why do the earliest merges look like letter pairs and the later
   ones like whole words? What is BPE actually learning?
   - Answer: ___
2. **Compression:** with 500 merges, what happened to tokens per word and
   vocabulary size? Why does the gain flatten?
   - Tokens per word at 500 merges: ___
   - Vocabulary size at 500 merges: ___
   - Why the gain flattens: ___
3. **Break it:** what did the tokenizer do with the digits and the Hindi word in
   "Call me at 98765 43210, dhanyavaad!"? What does that say about a tokenizer
   trained only on simple English stories?
   - Answer: ___
4. **Round trip:** did "McDonald ate a burger." round-trip? Why or why not?
   - Answer: ___

## What I would do differently next time

- ___
