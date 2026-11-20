# Findings: Chapter 7: SFT: Teaching a Model to Assist

Fill this in as you work. One line per question is enough, but each
line must trace to something you read or ran. The measured numbers
from the November 20, 2026 local runs are already filled in below;
your job is the reasoning, and the Colab run is the real exercise.

## Measured results (November 20, 2026 local runs)

- Loss demo (sft_loss_demo.py): one example, prompt "What is a DPIA?",
  response "A DPIA is a data protection impact assessment." Average
  loss on prompt tokens only: 0.179. SFT loss (response tokens only):
  0.523. Unmasked loss (all tokens): 0.400. Prompt tokens are 5 of 14
  but carry only 0.896 of 5.598 total loss. One confident mistake
  (p=0.05 on "data"): SFT loss 0.523 to 0.754; loss on that token
  alone 2.996.
- Dataset checks (dataset_checks.py): 40 training examples, 10 test
  prompts. Average prompt 6.2 words, average completion 41.7 words.
  0 exact duplicate prompts, 0 near-duplicates, 0 PII-shaped
  patterns. Test/train overlap: 4 verbatim overlaps in the first
  version (test-02, test-03, test-05, test-06), rewritten as
  paraphrases; re-check 0 overlaps.
- Rubric on worked examples (rubric.py): worked-01 base 1/8, SFT 8/8.
  worked-02 base 4/8, SFT 8/8. Mean totals: base 2.5/8, SFT 8.0/8.
  Worked examples are written for the lesson, not model outputs.
- Base model: TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T,
  1.1B parameters, 3T pre-training tokens. License: record it from
  the model card before downloading (Chapter 2 method).

## Exercise A: The loss demo (local, 15 minutes)

Run `python sft_loss_demo.py` and read `loss_demo_report.md`. Then
answer these in your own words:

1. **The numbers:** copy the three averages: prompt only, response
   only (SFT loss), all tokens. Which is lowest, and why is the
   lowest one the misleading one?
   - Prompt only: ___
   - Response only (SFT loss): ___
   - All tokens: ___
   - Why the lowest misleads: ___
2. **The dilution:** the prompt is 5 of 14 tokens but only 0.896 of
   5.598 total loss. What does that ratio say about where the
   training signal lives?
   - Answer: ___
3. **The confident mistake:** one token at p=0.05 moved the SFT loss
   from 0.523 to 0.754. What does that say about what SFT punishes
   hardest?
   - Answer: ___
4. **Say it back:** in two sentences, without looking at README
   section 2, explain what masked loss is and why SFT uses it. Then
   check your two sentences against section 2.
   - My two sentences: ___
   - Check: ___

## Exercise B: The Colab SFT run (about 30 minutes of compute)

Run `train_sft.py` on Colab, then `rubric.py --generations
generations.json`, and read `generations.json`. Then answer these:

1. **The training:** trainable parameters printed by the trainer,
   and the training loss at the start and the end.
   - Trainable parameters: ___
   - Loss start and end: ___
2. **The comparison:** rubric mean for the base arm and for the SFT
   arm, over all 10 test prompts.
   - Base mean: ___/8
   - SFT mean: ___/8
3. **The biggest gap:** which test prompt shows the largest
   base-vs-SFT difference, and which criterion drives it?
   - Prompt: ___
   - Criterion: ___
4. **The probes:** copy the base and SFT replies to test-07 (the
   Kenya AI Act) and test-08 (the phone number). Did the SFT model
   refuse to invent in both cases?
   - test-07 base: ___
   - test-07 SFT: ___
   - test-08 base: ___
   - test-08 SFT: ___
5. **The honest reading:** 40 examples teach format, not knowledge.
   Find one SFT reply that is well formatted but wrong or thin, and
   say what is wrong with it.
   - Prompt and reply: ___
   - What is wrong: ___
6. **Say it back:** in two sentences, explain the difference between
   a base model and an assistant, using one of your own generations
   as the example. Then check them against README section 1.
   - My two sentences: ___
   - Check: ___

## Exercise C: Dataset governance (20 minutes)

1. **The datasheet:** read `datasheet_sft.md`. Which section would
   change first if you added 40 more examples from real support
   chats, and why?
   - Answer: ___
2. **The Presidio run:** run Chapter 3 `pii_scrub.py` on
   `sft_data.jsonl`. How many spans did it flag, and were any of
   them real personal data?
   - Spans flagged: ___
   - Real personal data: ___
3. **The contamination catch:** the first test set had 4 verbatim
   overlaps with training. Say in one sentence why a test prompt
   that also appears in training is not a test.
   - Answer: ___
4. **The license:** record the TinyLlama base model license from the
   model card.
   - License: ___
5. **The pipeline order:** list the Chapter 2, 3, 4, and 6 gates this
   dataset passed, in order, and one thing each gate caught or
   proved.
   - Chapter 2: ___
   - Chapter 3: ___
   - Chapter 4: ___
   - Chapter 6: ___

## My SFT rule for this course

What I will always check before trusting an SFT model, and what a
good rubric score does and does not prove.
- Answer: ___
