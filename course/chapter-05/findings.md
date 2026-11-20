# Findings: Chapter 5: Pre-training at Toy Scale

Fill this in as you work. One line per question is enough, but each line must
trace to something you read or ran. The measured numbers from the November 18,
2026 smoke run are already filled in below; your job is the reasoning, and
the Colab run is the real exercise.

## Measured results (November 18, 2026 smoke run)

- Smoke corpus: 24 short stories written for this course, all fictional.
  4 exact duplicates planted, 4 stories carrying phone/email/number strings.
- Model: 2 layers, 2 heads, embedding dim 64, context 64, 111,360
  parameters.
- Vocabulary: 56 characters. Random-guess loss ln(vocab) = 4.03.
- Cleaning: 4 exact duplicates removed, 3 PII-like spans replaced in the
  training split. Train chars: raw 2,206, cleaned 1,743.
- Raw arm: step-1 train loss 3.699; final train loss 1.995, final
  validation loss 2.300.
- Cleaned arm: step-1 train loss 3.710; final train loss 1.960, final
  validation loss 2.218.
- Validation loss difference (raw minus cleaned): 0.083 in favour of
  cleaned, measured on just 2 validation stories, so not a finding.
- Samples: story-shaped fragments, not coherent English (for example,
  raw: "Once upon a timen as sked herd ighed hen").
- PII-like patterns in samples: raw arm 0, cleaned arm 0.

## Exercise A: The smoke test

1. **The baseline:** vocabulary size, ln(vocab), train loss at step 1,
   and how close it is to the random-guess baseline. What would a step-1
   loss far from the baseline suggest?
   - Vocabulary size: ___
   - Random-guess loss ln(vocab): ___
   - Train loss at step 1: ___
   - What it means: ___
2. **The curves:** final train and validation loss for each arm. Did both
   fall well below the baseline? Is validation above or below train, and
   what does the gap mean?
   - Raw: train ___, validation ___
   - Cleaned: train ___, validation ___
   - What the gap means: ___
3. **The ablation:** the validation loss difference between the arms. Is
   it a finding or noise? What does the train loss say about duplicated
   stories?
   - Difference: ___
   - Finding or noise: ___
   - Train loss and duplicates: ___
4. **The samples:** one sentence from each arm, what is right and wrong
   with it, and the PII-like pattern counts.
   - Raw sample sentence: ___
   - Cleaned sample sentence: ___
   - PII-like patterns: raw ___, cleaned ___

## Exercise B: Train on real TinyStories

1. **The curves:** at what step does validation loss stop falling? Is
   there a train/validation gap, and does it grow with steps?
   - Answer: ___
2. **The ablation, for real:** final validation loss per arm, the
   difference, stories removed, spans replaced. Consistent with the smoke
   test? Which result do you trust more, and why?
   - Raw final validation loss: ___
   - Cleaned final validation loss: ___
   - Stories removed by cleaning: ___
   - PII-like spans replaced: ___
   - Which I trust more, and why: ___
3. **The samples:** which model's stories are more coherent, one sentence
   that shows the difference, and the PII-like pattern counts.
   - More coherent: ___
   - Sentence that shows it: ___
   - PII-like patterns: raw ___, cleaned ___
4. **Scale:** what would you change first to close the gap to the
   10-million-parameter TinyStories result: more parameters, more stories,
   or more steps? One reason, and one cost.
   - Change first: ___
   - Reason: ___
   - Cost: ___

## Exercise C: The training-data summary

1. **My training-data summary** (under 200 words, Article 53(1)(d) shape):
   - Summary: ___
   - Could a stranger reproduce the run from it plus the script? What is
     missing?
     - Answer: ___
2. **The gap:** one thing that would have to change before this summary
   could serve a real general-purpose model.
   - Answer: ___
3. **The PII question:** which model would you ship if the training data
   had contained real personal data, and what would you have to prove
   before shipping the raw one?
   - Answer: ___

## My pre-training rule for this course

What I will record for every training run from now on (data, cleaning,
config, seed, losses), and what I will never train on without cleaning first.
- Answer: ___
