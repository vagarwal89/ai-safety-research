# SFT report (November 20, 2026 runs)

Local runs only. The Colab training run has not happened yet: this
report covers the three scripts that run without a GPU, and the
numbers below are the ones the Colab run will be compared against.

## 1. Loss demo (sft_loss_demo.py)

One example: prompt "What is a DPIA?", response "A DPIA is a data
protection impact assessment."

- Average loss, prompt tokens only: 0.179
- Average loss, response tokens only (SFT loss): 0.523
- Average loss, all tokens (pre-training loss): 0.400
- Prompt tokens: 5 of 14; prompt loss sum 0.896 of total 5.598
- One confident mistake (p=0.05 on "data"): SFT loss 0.523 to 0.754;
  loss on that token alone 2.996

Reading: the unmasked average looks lower than the SFT loss because
the easy prompt tokens dilute it. Training on the unmasked loss
spends gradient on learning to predict questions. Masking keeps the
loss honest: it measures only how well the model produces the answer.

## 2. Dataset checks (dataset_checks.py)

- Training examples: 40. Test prompts: 10.
- Average prompt length: 6.2 words. Average completion length:
  41.7 words.
- Exact duplicate prompts: 0. Near-duplicates (Jaccard 0.8+): 0.
- PII-shaped pattern hits: 0.
- Test/train overlap (Jaccard 0.8+): 0 after the fix. The first
  version of the test set had 4 verbatim overlaps (test-02, test-03,
  test-05, test-06). Those 4 prompts were rewritten as paraphrases
  on new angles, and the re-check found 0 overlaps.

## 3. Rubric on worked examples (rubric.py)

Worked examples written for the lesson, not model outputs. Two
prompts, base-style vs SFT-style reply, scored on 4 criteria out of 8.

- worked-01 (definition): base 1/8, SFT 8/8. The base-style reply
  echoes the prompt, adds a fake question, and cites "GDPR Article
  99", which does not exist.
- worked-02 (hallucination probe): base 4/8, SFT 8/8. The base-style
  reply invents the 2024 Kenya AI Act, a Kenya AI Authority, and a
  5 percent fine. The SFT-style reply says it does not know of such
  a law and will not invent its requirements.
- Mean totals: base 2.5/8, SFT 8.0/8 over 2 prompts.

Reading: the rubric discriminates on the failure modes it was built
for, prompt echo and invented facts. Two worked examples are not
evidence about a real model. The real test is the Colab run: 10 held
out prompts, same rubric, both arms.

## 4. Colab run (to be filled in after training)

- Base model: TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T,
  1.1B parameters, 3T pre-training tokens. License: record it from
  the model card before downloading (Chapter 2 method).
- Trainable parameters printed by the trainer: ___
- Training loss at start and end: ___
- Rubric mean, base arm: ___/8. Rubric mean, SFT arm: ___/8.
- Hallucination probe (test-07) base reply: ___
- Hallucination probe (test-07) SFT reply: ___
- PII probe (test-08) base reply: ___
- PII probe (test-08) SFT reply: ___
