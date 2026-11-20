# Chapter 5: Pre-training at Toy Scale

**Time:** ~90 minutes for the lesson, plus about 20 minutes of Colab training time.
**Needs:** a browser (Google Colab, free T4 GPU). Nothing installed locally.
**You will finish with:** a small GPT you trained yourself, two loss curves
(raw data vs cleaned data), generated stories from each model, and a
training-data summary written the way the EU AI Act asks for one.

**Builds on Chapter 3 and Chapter 4:** Chapter 3 cleaned the data (dedup,
PII scrub, BPE tokenizer) and Chapter 4 put a number on privacy (epsilon).
This chapter is where the cleaned data becomes a model. The question it
answers is the one Chapter 3 left open: does cleaning the data actually
change what the model learns? It feeds Chapter 6 (you will probe this very
model for memorized training data), Chapter 7 (SFT starts from a model
like this one), and Chapter 13 (DP-SGD is this same training loop with
noise added to the gradients, which is Chapter 4's idea applied to
training itself).

**How this chapter is written:** Chapter 3's tokenizer report was hard to
follow, so this chapter does the small version first and the real version
second. Every new idea gets a hand-worked example with tiny numbers you
can check on paper, before the script runs it at real scale. If a section
feels fast, stop and work the tiny example by hand. That is the lesson.

---

## 1. The one picture: a model is a next-token predictor

A language model does exactly one thing: given some text, it guesses what
comes next. Chat, code, reasoning, all of it is that one trick, repeated
over and over, at enormous scale. Pre-training is teaching the model that
trick by showing it a lot of text and correcting every guess.

```
TEXT SO FAR            MODEL'S JOB
"The cat sat on the"  -> guess the next token: "mat", "floor", "moon"?
```

The model does not know what a cat is. It knows statistics: in the stories
it read, "sat on the" is usually followed by "mat" or "floor", rarely by
"moon". Training is the process of adjusting the model's numbers until its
guesses match the statistics of the training text. Everything in this
chapter is a detail of that one sentence.

## 2. Worked example 1: text becomes numbers, then numbers become targets

Chapter 3 taught tokenization. This chapter uses the simplest tokenizer
there is: one character is one token. That is the same choice Karpathy's
nanoGPT makes in its fastest example, the character-level Shakespeare
model. The reason is teaching, not performance: with character tokens the
vocabulary is small enough to print, and every step below can be checked
by hand.

Take the sentence "The cat sat". As characters, it is 11 tokens:

```
text:   T  h  e     c  a  t     s  a  t
token:  0  1  2  3  4  5  6  7  8  9  10
```

(Those ids are made up for this example. The script builds the real ids
from the characters that actually appear in the training text.)

Training turns one sequence into many examples by sliding a window across
it. For the input "The cat sat", the target is the same text shifted one
step to the right:

```
input:   T  h  e     c  a  t     s  a
target:  h  e     c  a  t     s  a  t
```

Read it as 10 small lessons, not one big one. At position 0, the model
sees "T" and must guess "h". At position 3, it sees "The " and must guess
"c". At position 7, it sees "The cat " and must guess "s". Every position
is one prediction, and the model is scored on all of them at once. That is
why a single training step teaches so much: one window of 64 characters
contains 64 predictions.

Two things to notice. First, the model never sees the future: when it
guesses the token at position 7, it may only use positions 0 to 6. The
mask inside the model enforces that, and it is the reason the model can
generate text one token at a time later. Second, there is no separate
"label" file. The labels are the text itself, shifted by one. That is why
pre-training is called self-supervised: the data labels itself.

## 3. Worked example 2: an embedding is a lookup table

**Embedding** is the word this course uses for a simple idea: every token
id has a row of numbers attached to it, and the model learns those
numbers. The row is called a **vector**. Here is a toy embedding table
with 5 tokens and 4 numbers per token:

```
token id  token   vector (4 numbers)
0         "t"     [ 0.10, -0.20,  0.30,  0.00]
1         "h"     [ 0.20,  0.10, -0.10,  0.40]
2         "e"     [-0.30,  0.20,  0.10,  0.10]
3         " "     [ 0.00,  0.00,  0.10, -0.20]
4         "c"     [ 0.30, -0.10,  0.20,  0.20]
```

Looking up token 4 ("c") returns the row [0.30, -0.10, 0.20, 0.20].
That is all an embedding does: id in, row of numbers out. The model
starts with random numbers in this table, and training changes them.
Tokens that behave alike end up with similar rows. That is how the model
"knows" that "cat" and "dog" are more alike than "cat" and "kite": their
rows end up pointing in similar directions.

The real model in this chapter has an embedding dimension of 64 in smoke
mode and 128 on Colab, so each row has 64 or 128 numbers instead of 4.
The idea is identical, and the table is the first thing the model learns.
There is a second table just like it for **positions**: the model adds a
position vector to each token vector, so it knows whether a token is first,
fifth, or fiftieth in the window. Without that, "cat sat" and "sat cat"
would look the same.

How tokens, embeddings, and vectors are used in training, in one
paragraph: the model turns each input token into its embedding vector,
passes the vectors through the transformer blocks (section 6), and
produces one output vector per position. The output vector is scored
against every token in the vocabulary, and the best-scoring tokens are
the model's guesses for the next token. Training adjusts the embedding
table and every other number in the model so the right token scores
higher next time.

## 4. Worked example 3: logits, softmax, and the guess

After the transformer blocks, the model holds one vector per position.
A final linear layer turns each vector into one number per vocabulary
token. Those numbers are called **logits**: raw scores, one per possible
next token. A logit of 2.0 means "I like this token", a logit of 0.0
means "I am neutral", a logit of -3.0 means "I dislike this token".
Logits are not probabilities: they can be negative, and they do not add
up to 1.

**Softmax** turns logits into probabilities. Take three logits,
[2.0, 1.0, 0.0], for three candidate next tokens:

```
e^2.0 = 7.39     e^1.0 = 2.72     e^0.0 = 1.00
sum = 7.39 + 2.72 + 1.00 = 11.11
probabilities = 7.39/11.11, 2.72/11.11, 1.00/11.11
              = 0.665, 0.245, 0.090
```

Now the model has said something checkable: the first token gets 66.5%
of the probability, the second 24.5%, the third 9.0%. To generate text,
the script samples from these probabilities (or takes the highest one).
To train, it compares them with the truth, which is section 5.

Softmax is also why the vocabulary size matters: with 65 characters,
the model spreads its probability over 65 options. With a 50,000-token
BPE vocabulary, it spreads over 50,000. That is why Chapter 3's BPE
tokenizer changes what training feels like: fewer, longer tokens mean
each prediction carries more information, and the loss numbers are not
directly comparable across tokenizers.

## 5. Worked example 4: loss, by hand

**Loss** is the model's error score for one prediction. For next-token
prediction it is **cross-entropy loss**: the negative log of the
probability the model gave to the true next token.

```
loss = -ln(probability of the true next token)
```

Use the probabilities from section 4. If the true next token is the
first one, which the model gave 66.5%:

```
loss = -ln(0.665) = 0.41
```

If the model had given the true token only 9.0%:

```
loss = -ln(0.090) = 2.41
```

A confident correct guess scores near 0. A confident wrong guess scores
high. A model that knows nothing spreads its probability evenly. With 65
characters, each token gets 1/65, and the loss is:

```
loss = -ln(1/65) = ln(65) = 4.17
```

That number, 4.17, is the baseline every run in this chapter is measured
against. Before training, the loss should be near 4.17. If your run
starts at 4.17, the model is correctly clueless. If it starts at 0.5,
something is leaking the answers. The training loss the script prints is
the average of this per-position loss over a batch of windows.

A second number helps you read loss: **perplexity**, which is e raised
to the loss. A loss of 1.47 (the nanoGPT Shakespeare result) is a
perplexity of e^1.47 = 4.35, which reads as "on average, the model is
choosing among about 4 plausible next characters." A loss of 4.17 is a
perplexity of 65: choosing among all of them. Lower loss means fewer
plausible next tokens, which means the model has learned the patterns.

## 6. Attention, in plain words

The transformer block is the only complicated part of the model, and
only one piece of it needs a plain-English explanation: **attention**.
When the model predicts the token after "The cat sat on the", it should
pay more attention to "cat" than to "the", because "cat" is what decides
between "mat" and "moon". Attention is the mechanism that lets each
position look back at earlier positions and decide which ones matter for
its prediction. Each position computes a score against every earlier
position, turns the scores into weights with a softmax, and takes a
weighted average of the earlier positions' vectors. That average is the
context the position uses to predict.

Three details matter for the rest of the course. First, the scores are
learned: the model learns which earlier words to attend to, it is not
told. Second, attention is **causal**: a position may only attend to
positions before it, never after, which is what makes generation work
one token at a time. Third, there are several attention **heads** in
parallel (2 in smoke mode, 4 on Colab), so different heads can track
different things, one for grammar, one for the story's characters, and
so on. The rest of the block, a small feed-forward network applied to
each position on its own, plus layer normalization, is plumbing. You do
not need its internals to read a loss curve.

## 7. The training loop: four steps, repeated

Training is one loop, repeated hundreds or thousands of times:

1. **Forward pass.** Take a batch of windows, run them through the
   model, get a probability for the next token at every position.
2. **Loss.** Compare the probabilities with the true next tokens
   (section 5) and average. One number.
3. **Backward pass.** Compute how much each number in the model
   contributed to the loss, and in which direction changing it would
   reduce the loss. This is **backpropagation**: the chain rule from
   calculus, applied mechanically to every weight. You do not compute
   it by hand; PyTorch does. What matters is what it means: every
   weight gets a gradient, a small arrow saying "move me this way".
4. **Optimizer step.** Move every weight a small amount in the
   direction its gradient points. The optimizer here is **AdamW**, the
   standard choice for transformers. It keeps a running average of
   recent gradients per weight, so weights that get noisy gradients
   move in smaller steps and weights that get steady gradients move
   in larger ones. The **learning rate** sets the overall step size:
   3e-3 in smoke mode, 1e-3 on Colab. Too large and training jumps
   around and diverges; too small and it crawls. The script also decays
   the learning rate linearly to 10% of its starting value over the
   run, which is a standard way to settle the model down at the end.

One step changes the weights by a tiny amount. A thousand steps change
them a lot. The loss curve is the record of that change.

## 8. How to read a loss curve

The script prints train loss and validation loss every 25 steps (smoke)
or 50 steps (Colab). **Train loss** is measured on text the model is
learning from. **Validation loss** is measured on held-out stories the
model never trains on. Read them together:

- Both falling: the model is learning general patterns. This is what
  you want to see.
- Train falling, validation flat: the model has learned what it can
  from this much data. More steps will not help much.
- Train falling, validation rising: the model is **overfitting**. It is
  memorizing the training stories instead of learning patterns that
  transfer. The gap between the two curves is the memorization gap,
  and Chapter 6 measures it directly with an extraction probe.
- Both flat near the random baseline (4.17 here): the model is not
  learning. Check the learning rate and the data loading before
  anything else.

The validation stories in this chapter are the last 10% of the loaded
stories, split off before any cleaning, so no validation story is ever
trained on. The cleaned arm and the raw arm are both evaluated on the
same cleaned validation text, so the comparison is apples to apples.

## 9. What this run measured (November 18, 2026)

`train.py --smoke --arm both` ran on the built-in toy corpus (24 short
stories, all fictional, 4 exact duplicates planted, 4 stories carrying
phone/email/number strings). Tiny model: 2 layers, 2 heads, embedding
dimension 64, context window 64, 111,360 parameters. Vocabulary: 56
characters. Random-guess loss ln(56) = 4.03.

| arm | step-1 train loss | final train loss | final validation loss |
|---|---|---|---|
| raw | 3.70 | 1.995 | 2.300 |
| cleaned | 3.71 | 1.960 | 2.218 |

Cleaning removed 4 exact duplicates and replaced 3 PII-like spans in
the training split (a fourth PII-like span sat in the validation split,
which is cleaned separately). Training characters fell from 2,206 raw
to 1,743 cleaned. The validation loss difference is 0.083 in favour of
cleaned, measured on just 2 validation stories, so it is not a finding:
a re-run with a different seed could flip it. Both arms fell far below
the 4.03 random baseline, and in both arms the validation loss sits
above the train loss (2.30 vs 2.00 raw, 2.22 vs 1.96 cleaned), which is
the normal generalization gap. The step-1 losses (3.70 and 3.71) sit
close to the 4.03 baseline, which is what a correctly clueless model
looks like.

Two things to notice. First, the cleaned arm's train loss fell slightly
faster than the raw arm's (1.960 vs 1.995), which is the opposite of the
textbook expectation that duplicates make train loss fall faster. At
this scale the effect is small and inconsistent, and that is itself the
lesson: with 22 training stories, do not expect a clean ablation
signal. Second, the samples are story-shaped fragments, not coherent
English: "Once upon a timen as sked herd ighed hen" from the raw model,
"Once upon a timend hed nd haind plled poun" from the cleaned model.
After 150 steps on 24 stories, the model has learned letter patterns
and story openings, not stories. Neither arm's samples contained any
PII-like patterns (0 for both), which at this scale proves nothing: with
120 sampled characters and a tiny model, absence is expected either way.
The smoke run is a correctness check, not a finding about TinyStories:
24 stories cannot support a claim about 2.7 million. The Colab run is
the real exercise, and its numbers belong in your findings.

### The data at real scale

TinyStories (Eldan and Li, 2023, arXiv 2305.07759) is a synthetic
dataset of short stories written by GPT-3.5 and GPT-4, using only words
a typical 3 to 4 year old would know. The first version has about 2.1
million stories; the second version, generated by GPT-4 alone, has
2,717,495 stories and about 543 million tokens under a 4,096-token
vocabulary. The authors trained models from 1 million to 33 million
parameters and showed that a model with as few as 10 million parameters
can produce coherent English with near-perfect grammar on this data.
That is why it is the right dataset for this chapter: the task is small
enough for a toy model to actually learn it, and the result is readable
English, so you can judge the samples by eye.

License, corrected: TinyStories is CDLA Sharing 1.0, which permits
commercial use, with share-alike on published data. Chapter 2's earlier
note about a conflicting CC BY-NC 4.0 label was wrong; the metadata and
the paper's own table both say CDLA Sharing 1.0.

For scale, the reference point is nanoGPT's character-level Shakespeare
run (Karpathy's nanoGPT repository): 6 layers, 6 heads, 384 embedding
dimensions, about 10.7 million parameters, trained on about 1 million
characters, reaching a validation loss of about 1.47 in about 3 minutes
on a GPU. Your Colab model is smaller (about 800,000 parameters), and
your data is simpler, so expect a lower loss than 1.47 and a shorter run.

## 10. The ablation: cleaned vs raw

The script trains two models with the same seed and the same config,
one on the raw stories and one on the cleaned stories (exact duplicates
removed, phone/email/number spans replaced with placeholders). Three
things are compared: final validation loss, the shape of the loss
curves, and the generated samples, including a count of PII-like
patterns (digit runs, email shapes) in the samples.

What to expect, honestly: at toy scale the validation loss difference
will probably be small, and with a validation set of only a few stories
it is noise, not a finding. The smoke run's validation set is 2 stories,
so even a difference of 0.08 would not be resolvable. Duplicated stories
can make the raw arm's train loss look better, because the model
memorizes the repeated text and predicts it easily, but in this run the
cleaned arm's train loss actually fell slightly faster, which shows the
effect is small and inconsistent at this scale. That is the lesson, not
a failure: a lower train loss on duplicated data is memorization, not
learning, and the validation curve is what exposes it. The cleaning
effect that matters most does not show up in the loss at all: the
cleaned arm never saw the phone numbers and email addresses, so it
cannot reproduce them. Chapter 6 tests that claim with an extraction
probe on this very model.

## 11. The regulation hook: training is where the data becomes the model

### EU AI Act, Article 10(2)(c) and (e): preparation and suitability

Chapter 3 covered Article 10(2)(c), which names the preparation
operations: annotation, labelling, cleaning, updating, enrichment, and
aggregation. This chapter is where those operations pay off or fail:
the training run is the evidence that the preparation happened, and the
loss curves are the evidence of whether it was enough. Article 10(2)(e)
requires examining the availability, quantity, and suitability of the
datasets. The ablation is that examination in miniature: is 2,000
stories enough for this model, and is the cleaned set more suitable
than the raw set? A training report that cannot answer those questions
is not a data governance record, it is a training log.

### EU AI Act, Article 10(3): the quality bar, applied to training

Article 10(3) requires training, validation, and testing datasets to be
relevant, sufficiently representative, and to the best extent possible
free of errors and complete. Training is the stage where a violation
shows up as a number: unrepresentative data gives a validation loss
that will not fall; error-filled data gives a model that reproduces the
errors. The validation split is part of the Article 10(3) evidence: it
is the held-out check that the training data was representative of
something beyond itself.

### EU AI Act, Article 53(1)(d): the training-content summary

For general-purpose AI models, Article 53(1)(d) requires the provider
to draw up and make publicly available a sufficiently detailed summary
of the content used for training, following the template provided by
the AI Office. The duty has applied since August 2, 2025, and the
open-source exemption in Article 53(2) does not cover it: an
open-source model provider must still publish the summary. Annex XI
adds that the technical documentation must describe the training data:
its type and provenance, curation methods, the number of data points,
and how it was obtained and selected. Exercise C writes that summary
for your toy model. It is a small document, but it is the same shape
as the real one: sources, size, processing, and what was removed.

### GDPR, Article 5(1)(c): minimization at the source

Chapter 4 framed differential privacy as minimization by bounding what
can be learned. Training adds the other half of the argument: a model
trained on raw personal data carries that data in its weights, and
weights are much harder to clean than a dataset. Removing personal data
before training is minimization at the source, and it is cheaper than
any fix after training. Chapter 6 will show why: once the model has
memorized a phone number, the only reliable fix is retraining without it.

### California AB 2013: the same idea, in US law

California's AB 2013 requires developers of generative AI systems
released on or after January 1, 2022, and made publicly available to
Californians, to post a training-data summary (12 items), in force
since January 1, 2026. The EU summary and the California summary ask
for the same kind of record: what the model was trained on, and where
it came from. If you can write one, you can write the other.

## 12. Lab setup (10 minutes)

Run this in Colab. PyTorch is preinstalled on Colab, so there is no
install step for the model itself. The script needs the `datasets`
library only to stream TinyStories.

1. Open https://colab.research.google.com and start a new notebook.
2. In the first cell, install the data library:
   ```python
   !pip install -q datasets
   ```
   (The `!` prefix means "run this as a shell command, not as Python."
   A cell starting with `!` runs in the terminal. If you paste a shell
   command into a Python cell, Colab will complain about the syntax,
   because `pip install` is not Python. This is the same rule as
   Chapter 3.)
3. Upload `train.py` from this folder, or paste it into a cell.
4. Run the smoke test first, so you know the script works before you
   spend GPU time:
   ```python
   !python train.py --smoke --arm both
   ```
5. Then run the real exercise:
   ```python
   !python train.py --arm both --stories 2000 --steps 1500
   ```
   On a free T4 this takes roughly 15 to 25 minutes for both arms. The
   script writes `training_report.md` and `loss_curve.csv` in the same
   folder, and saves both trained models under `out/`.
6. If the network call to Hugging Face fails, the script falls back to
   the toy corpus and says so clearly in its report. A report that says
   "TOY CORPUS fallback" is a smoke-test report, not a TinyStories
   result. Re-run when the network is back.

## 13. Exercise A: Run the smoke test and check the numbers (20 minutes)

Run `!python train.py --smoke --arm both` and read
`training_report.md`. Then answer these in `findings.md`:

1. **The baseline:** what is the vocabulary size, and what is ln(vocab)?
   What was the train loss at step 1, and how close is it to the
   random-guess baseline? If it is far from the baseline at step 1,
   what would that suggest?
2. **The curves:** copy the final train and validation loss for each
   arm. Did both arms fall well below the random baseline? Is the
   validation loss above or below the train loss for each arm, and what
   does that gap mean?
3. **The ablation:** what is the difference in final validation loss
   between the raw arm and the cleaned arm? How many validation stories
   is that difference measured on, and is it big enough to call a
   finding at that scale? What does the train loss say: which arm's
   train loss fell faster, and what does that tell you about what
   duplicated stories do at this scale?
4. **The samples:** read the generated samples from both arms. Do they
   read like stories? Pick one sentence from each arm and say what is
   right and what is wrong with it. How many PII-like patterns did each
   arm's samples contain?

## 14. Exercise B: Train on real TinyStories and read the curves (30 minutes)

Run `!python train.py --arm both --stories 2000 --steps 1500` and read
`training_report.md` and `loss_curve.csv`. Then answer these in
`findings.md`:

1. **The curves:** plot or sketch train and validation loss against
   step for both arms (the CSV has the numbers). At what step does the
   validation loss stop falling? Is there a train/validation gap, and
   does it grow with steps?
2. **The ablation, for real:** what is the final validation loss for
   each arm, and the difference? How many stories did cleaning remove,
   and how many PII-like spans did it replace? Is the loss difference
   consistent with the smoke test, or different? Say which result you
   trust more, and why.
3. **The samples:** generate from the prompt "Once upon a time" with
   each model. Which model's stories are more coherent, and can you
   point to a specific sentence that shows the difference? Count the
   PII-like patterns in each model's samples. Did the cleaned model
   produce fewer?
4. **Scale:** the Colab model has about 800,000 parameters. TinyStories
   was shown to work with 10 million. Your model is 12 times smaller
   than that. What would you change first to close the gap: more
   parameters, more stories, or more steps? Give one reason for your
   choice, and one cost of it.

## 15. Exercise C: Write the training-data summary (20 minutes)

Write a training-data summary for your Colab model, in the shape of an
Article 53(1)(d) summary, under 200 words. It must state: the data
source (TinyStories, version, license), the number of stories and
characters trained on, the cleaning steps and what they removed, the
model size and training steps, and the validation loss. Then answer in
`findings.md`:

1. **The summary:** paste it. Could a stranger reproduce your training
   run from it plus the script? What is missing?
2. **The gap:** Article 53(1)(d) summaries are for general-purpose
   models placed on the EU market. Your toy model is not one. Name one
   thing that would have to change before this summary could serve a
   real model: for example, the data provenance, the evaluation, or the
   disclosure of copyrighted material.
3. **The PII question:** your cleaned model never saw the phone numbers
   and email addresses. Your raw model did. Which model would you ship
   if the training data had contained real personal data, and what
   would you have to prove before shipping the raw one? (Chapter 6
   gives you the test.)

## 16. What to push to GitHub

In `course/chapter-05/`:
- `README.md`: this file.
- `train.py`: the training script (already here; run it).
- `training_report.md`, `loss_curve.csv`: the script outputs.
- `out/model_raw.pt`, `out/model_cleaned.pt`: the trained weights. They
  stay local: they are binary files, and the snapshot push used for
  this course handles text files only. The report and the loss curve
  carry the results; note the checkpoint location here if you retrain
  at larger scale, and do not commit large checkpoints.
- `findings.md`: your answers: the four Exercise A questions, the four
  Exercise B questions, and the three Exercise C questions.

## 17. Check yourself

1. What does a language model predict, and why is the target the input
   shifted by one?
2. What is an embedding, and what does the model learn in the embedding
   table?
3. Work it by hand: logits [3.0, 0.0, 0.0] for three tokens. What are
   the probabilities? What is the loss if the true token is the first?
   What is the loss if the true token is the second?
4. What is the random-guess loss for a vocabulary of 50 tokens, and how
   do you compute it?
5. What is the difference between train loss and validation loss, and
   what does a rising validation loss with a falling train loss mean?
6. Why does the cleaned arm sometimes show a higher train loss than the
   raw arm, and why is that not necessarily bad?
7. What does Article 53(1)(d) require, and does the open-source
   exemption in Article 53(2) remove that duty?

## 18. Paper seed

Your training report is the seed of a methods paper: "Cleaning before
training at toy scale: what dedup and PII scrubbing do to a small GPT."
The contribution is the measurement, not the model: a controlled
ablation with identical seeds and configs, loss curves for both arms,
and a sample-level check for PII-like reproduction. The honest result
is likely to be "the loss difference is within noise, and the
memorization difference is the finding", which is a stronger paper than
a claimed loss win. Keep the report, the loss curves, the seeds, and
the checkpoints. Chapter 15 turns your best lab into a paper, and a
paper that reports a null result on loss with a positive result on
memorization is exactly the kind of careful claim reviewers trust.

## Key terms (first-use glossary)

- **Pre-training:** training a model on a large body of text by teaching
  it to predict the next token, before any instruction tuning or
  alignment. The model from this chapter is a pre-trained model.
- **Next-token prediction:** the task of guessing the token that follows
  the text seen so far. The only task a language model is trained on.
- **Token id:** the integer a tokenizer assigns to a token. The model
  reads token ids, never raw text.
- **Embedding:** a table with one row of numbers (a vector) per token
  id. Looking up a token returns its row. The rows are learned during
  training.
- **Vector:** a list of numbers that represents a token, a word, or a
  position inside the model. Similar meanings end up with similar
  vectors.
- **Logits:** the raw scores the model assigns to each possible next
  token, before they are turned into probabilities.
- **Softmax:** the function that turns logits into probabilities: it
  exponentiates each logit and divides by the sum, so the results are
  positive and add up to 1.
- **Cross-entropy loss:** the negative log of the probability the model
  gave to the true next token. Lower is better; the random-guess value
  is ln(vocabulary size).
- **Perplexity:** e raised to the loss. It reads as the average number
  of plausible next tokens the model is choosing among.
- **Attention:** the mechanism that lets each position look back at
  earlier positions and weight them by relevance when predicting the
  next token. Causal attention only looks backward.
- **Transformer block:** one layer of the model: attention plus a small
  feed-forward network, with layer normalization. Blocks are stacked
  to make the model deeper.
- **Backpropagation:** the algorithm that computes how much each weight
  contributed to the loss, so the optimizer knows which way to move it.
- **Optimizer (AdamW):** the algorithm that updates the weights each
  step, using the gradients and the learning rate.
- **Learning rate:** the overall step size for weight updates. Too large
  and training diverges; too small and it crawls.
- **Overfitting:** memorizing the training data instead of learning
  patterns that transfer. It shows up as train loss falling while
  validation loss rises.
- **Validation loss:** loss measured on held-out data the model never
  trains on. The honest measure of whether the model learned anything
  general.
- **Ablation:** an experiment that changes one thing (here, cleaned vs
  raw data) and holds everything else fixed, to isolate that thing's
  effect.
