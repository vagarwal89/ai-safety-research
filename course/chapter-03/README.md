# Chapter 3: Data Prep That Holds Up

**Time:** ~90 minutes. **Needs:** a browser (Google Colab), nothing installed locally.
**You will finish with:** a near-duplicate pass over TinyStories, a PII scrub with a
measured recall, a working BPE tokenizer trained from scratch, and a cleaning record
that maps to EU AI Act Article 10(2)(c).

**Builds on Chapter 2:** the license audit found TinyStories is CDLA Sharing 1.0, which
permits commercial use, with share-alike on published data. Now you clean it. This chapter is the
Measure phase applied to preparation: every cleaning step gets a number attached to it,
because a cleaning step without a measurement is a claim, not evidence. It feeds
Chapter 5 (you will train on the cleaned data) and Chapter 6 (dedup is your first
defense against memorization).

---

## 1. The one picture: three gates

Raw data goes through three gates before it is allowed near a model:

```
RAW DATA  ->  [1. DEDUP]  ->  [2. PII SCRUB]  ->  [3. TOKENIZE]  ->  TRAINING DATA
```

1. **Dedup** removes copies. A story the model sees ten times is ten times more
   likely to be memorized, and ten times the wasted compute.
2. **PII scrub** removes personal data. A scrubber that misses names is a privacy
   failure; a scrubber that deletes ordinary words is a data quality failure.
3. **Tokenize** turns text into token ids, the integers the model actually reads.
   The tokenizer decides how long a text becomes and what the model can represent.

Each gate changes the data. Each change must be recorded: what you removed, what you
kept, and how you measured it. That record is the Article 10(2)(c) preparation record.

## 2. Gate 1: near-duplicates and MinHash

### Exact duplicates are easy. Near-duplicates are the real problem.

An exact duplicate is the same text twice: a hash of the text catches it. A
near-duplicate is the same story with a word changed, a sentence reordered, or a
different ending. Web data is full of them: the same article copied across sites,
the same story retold, the same template filled in differently. Exact matching
misses all of them.

### Jaccard similarity

Take two stories and turn each into a set of **shingles**: short overlapping
sequences of words. This chapter uses word 5-grams, so "the little cat sat on"
is one shingle, "little cat sat on the" is the next. The **Jaccard similarity**
of two stories is the size of the overlap of their shingle sets divided by the
size of their union:

```
Jaccard(A, B) = |A and B| / |A or B|
```

Identical stories score 1.0. Stories with nothing in common score 0. Two stories
that differ by one word score high, because most of their 5-grams are unchanged.
One changed word breaks only the five shingles that contain it.

### The MinHash trick

Computing exact Jaccard for every pair of stories is too slow at scale: a million
stories means about 500 billion pairs. **MinHash** (Broder, 1997) replaces each
shingle set with a short **signature** that preserves similarity. The idea: hash
every shingle with a hash function, keep only the minimum hash value. Do that with
64 different hash functions and you have a 64-number signature. Two similar sets
tend to have the same shingle winning the minimum under each hash function, so the
fraction of signature positions that agree estimates the Jaccard similarity. More
hash functions make the estimate tighter. Production pipelines use hundreds of
hashes, plus a technique called LSH banding to avoid comparing every pair at all.
RefinedWeb, the dataset behind the Falcon models, removes near-duplicates with
MinHash (Penedo et al., 2023).

### What this run measured (November 16, 2026)

`dedup.py` ran on the first 60 TinyStories with 5-gram shingles, 64 hash functions,
and a threshold of 0.7 estimated Jaccard. It found **0 near-duplicate pairs**. The
most similar pair in the sample scored 0.094 estimated against 0.028 exact. Two
things to notice. First, this slice of TinyStories is already diverse at the
5-gram level: short synthetic stories rarely share five-word runs. Second, the
estimate overshoots at low similarity: 0.094 against a true 0.028. With 64 hashes
the estimate is coarse, and it is most useful near the threshold, not far below it.

The same script on the embedded fallback sample, where duplicates are planted,
catches them exactly as designed: the identical pair scores 1.0, the one-word-change
pair scores 0.844 estimated against 0.773 exact, and the pair that shares an opening
but changes the ending stays below the threshold. The dedup pass keeps 12 of 14
stories and removes 2. That is the controlled demonstration: the method works, and
the threshold decides what counts as a copy. A story that shares an opening but ends
differently is arguably a different story, and a threshold of 0.7 says so.

## 3. Gate 2: PII scrub, and why recall is the number that matters

### Detection is not anonymization

A PII scrub has two parts. **Detection** finds personal data in text. **Anonymization**
replaces it with a placeholder such as `<PERSON>` or `<PHONE_NUMBER>`. Presidio splits
the job exactly this way: the Analyzer detects, the Anonymizer replaces. Chapter 1
used the Analyzer alone. This chapter runs both, and measures the result.

### Recall, precision, and the trade between them

- **Recall:** of all the personal data in the text, how much did you remove? A miss
  is personal data left in your training set.
- **Precision:** of all the things you removed, how many were actually personal data?
  A false positive deletes real meaning from your data.

A scrubber can have perfect recall and terrible precision: delete every word and
you removed all the PII, along with the dataset. The honest report gives both numbers
and the list of mistakes. Chapter 1 found the pattern on five samples: nicknames,
indirect identifiers, and partial identifiers are the hard cases. This chapter
measures them on eight labeled texts.

### What this run measured (November 16, 2026)

`pii_scrub.py` ran Presidio with the small spaCy model plus two custom recognizers
added by the script, one for UPI ids and one for employee ids. It found **16 of 16**
expected entity spans (100% recall by span overlap) and got the type right for
**14 of 16** (88%). The two wrong types are the interesting result, and they are
both indirect identifiers:

- The card ending 1761 was removed, but only because it looked like a date. If the
  digits had been shaped differently, it would have survived. A detector that removes
  something for the wrong reason is not a reliable control.
- The age plus role plus city combination ("the 45-year-old manager from Kent") was
  broken up, but only because its pieces looked like a date and a name. The combination
  is what identifies the person, and no single-entity detector can see a combination.

The false positives matter just as much. The word "Email" at the start of a sentence
was tagged as a person, "UPI" was tagged as a nationality, and "Meet Sara" was
swallowed whole into one person entity. Every false positive deletes real meaning.
And the custom recognizers earned their place: the UPI id and the employee id were
both found with the right type only because the script adds recognizers for them. A
US-tuned default knows neither shape. That is the general rule: a scrubber is only as
good as its fit to your data.

## 4. Gate 3: tokenization, or what the model actually sees

### A model never sees words

A model reads integers called **token ids**, drawn from a fixed **vocabulary**. The
**tokenizer** decides how text becomes those integers. Most modern tokenizers use
**Byte Pair Encoding (BPE)**, from Sennrich et al., 2016. GPT-2 uses a byte-level
variant of it. The idea is simple: start with single characters, then repeatedly
merge the most frequent adjacent pair. Frequent patterns get short codes, rare words
stay long. "The" becomes one token, "xylophone" becomes many pieces, and no word is
ever unrepresentable, because an unknown word falls back to single characters.

### Why the tokenizer belongs in a cleaning chapter

Three numbers follow from the tokenizer. **Tokens per word** decides how much text
fits in the context window and how much training costs. **Vocabulary coverage**
decides which languages and formats the model handles cheaply: a tokenizer trained
on simple English stories splits technical or non-English text into many more pieces.
**Weird splits** decide what the model finds easy to learn: if "ing" is one token
and "ed" is another, the model sees verb endings as units. The tokenizer is trained
on data, so it is part of the preparation record, not an afterthought.

### What this run measured (November 16, 2026)

`bpe_tokenizer.py` trained BPE from scratch on 100 TinyStories (14,929 words, 1,431
unique words) with 100 merges. Vocabulary size: **127 tokens**. The first merges are
the most common letter pairs in the corpus: "e" plus end-of-word, "d" plus end-of-word,
"th", "t" plus end-of-word. By merge 25 the tokenizer has learned whole words:
"was", "they", "all". Three test sentences encoded to **48 tokens for 21 words, 2.29
tokens per word**, and all three decoded back exactly. The unseen word "xylophone"
was split into single letters and small pieces ("x", "y", "lo", "p", "h", "one")
instead of failing. That fallback is the safety net that makes BPE work on any text.

## 5. The regulation hook: Article 10(2)(c) and Article 10(3), plus GDPR

### EU AI Act, Article 10(2)(c): preparation operations

Article 10(2) lists eight data governance practices for high-risk AI systems, and
(c) names the operations this chapter performs: "data preparation operations such as
annotation, labelling, cleaning, updating, enrichment and aggregation." The law does
not prescribe a threshold or a tool. It requires that the operations exist, are
appropriate to the intended purpose, and are documented. Your three scripts and
their three reports are that documentation: the dedup threshold, the scrub recall,
and the tokenizer vocabulary are the evidence that preparation happened and how.

### EU AI Act, Article 10(3): the quality bar

Article 10(3) requires training, validation, and testing datasets to be relevant,
sufficiently representative, and to the best extent possible free of errors and
complete, with appropriate statistical properties for the intended purpose. Each gate
serves one part of that bar. Dedup serves completeness and representativeness: copies
overweight one story and crowd out others. The scrub serves the error side: personal
data in training data is a defect, not a feature. Tokenization serves the statistical
properties: the token distribution is what the model actually learns from.

### EU AI Act, Article 10(2)(f) and (g): cleaning has a fairness cost

Article 10(2)(f) requires examining datasets for biases that could lead to
discrimination, and (g) requires measures to address them. Cleaning is where that
duty bites, because aggressive filtering removes some text at higher rates than
others. Dodge et al. (2021) showed that quality filters on web text remove some
dialects and identity-related text at higher rates than average. A dedup threshold
or a quality filter that silently deletes minority dialects makes the dataset less
representative, which is exactly what Article 10(3) forbids. Record what your
cleaning removed, and ask who it removed it from. Chapter 12 returns to this with
the full fairness pipeline.

### GDPR, Article 5(1)(c) and (d): minimization and accuracy

GDPR Article 5(1)(c) requires personal data to be adequate, relevant, and limited
to what is necessary for the purpose. That is data minimization, and the scrub is
its enforcement: every entity you remove is data you no longer hold without a
purpose. Article 5(1)(d) requires personal data to be accurate and kept up to date.
A scrubber that mislabels a card ending as a date is an accuracy problem in miniature:
the data is gone, but the record of what was removed is wrong, and the next person
to audit the pipeline will be misled. Report the wrong types, not just the recall.

## 6. Lab setup (10 minutes)

Run this in Colab. The scripts need three libraries, and Presidio needs the small
spaCy model. One detail worth knowing: Presidio defaults to the large spaCy model
(en_core_web_lg) and will try to download it if it is missing. The scripts in this
chapter point Presidio at the small model instead, which is what you install here.

1. Open https://colab.research.google.com and start a new notebook.
2. In the first cell, install the tools this chapter needs:
   ```python
   !pip install -q datasets presidio-analyzer presidio-anonymizer spacy
   !python -m spacy download en_core_web_sm
   ```
   (The `!` prefix means "run this as a shell command, not as Python." In Colab,
   a cell starting with `!` runs in the terminal. A cell without it runs Python.
   If you paste a shell command into a Python cell, Colab will complain about
   the syntax, because `pip install` is not Python.)
3. Upload the three scripts from this folder, or paste each one into a cell.
4. Run them one at a time:
   ```python
   !python dedup.py
   !python pii_scrub.py
   !python bpe_tokenizer.py
   ```
5. Each script writes a report in the same folder: `dedup_report.md`,
   `scrub_report.md`, `tokenizer_report.md`. If the network call to Hugging Face
   fails, each script falls back to a small embedded sample and says so clearly
   in its report. The fallback samples are short stories written for this course,
   not real TinyStories rows, and the dedup fallback has planted near-duplicates
   so you can see the method catch them.

## 7. Exercise A: Run the dedup pass (25 minutes)

Run `dedup.py` and read `dedup_report.md`. Then answer these in `findings.md`:

1. **Live sample:** how many near-duplicate pairs did it find in 60 stories, and
   what was the most similar pair (estimated and exact Jaccard)? What does a zero
   result mean here: clean data, or a threshold that is too strict for short stories?
2. **Fallback sample:** the script's planted duplicates score 1.0 (identical) and
   0.844 estimated against 0.773 exact (one word changed). The pair that shares an
   opening but changes the ending stays below the threshold. Is that the right call?
   Would you want that pair removed or kept, and why?
3. **Threshold:** lower THRESHOLD to 0.5 in the script and re-run. How many pairs
   appear, and what do they look like? Now raise it to 0.9. What disappears? Write
   down the threshold you would pick for the full 2.1 million TinyStories, and one
   sentence of reasoning. There is no single right answer; the reasoning is the
   deliverable.
4. **Scale:** this script compares every pair, which is fine for 60 stories and
   impossible for 2 million. In one paragraph, explain why MinHash plus LSH banding
   fixes that: what does banding let you skip, and what does it cost you?

## 8. Exercise B: Run the PII scrub and read the mistakes (25 minutes)

Run `pii_scrub.py` and read `scrub_report.md`. Then answer these in `findings.md`:

1. **Recall:** 16 of 16 expected spans were removed, 14 of 16 with the right type.
   Name the two wrong types. For each one, say whether the personal data was still
   removed, and whether you would trust the scrubber to remove the same shape of
   data next time.
2. **False positives:** the run tagged "Email" as a person, "UPI" as a nationality,
   and swallowed "Meet Sara" into one entity. Pick one and explain what it does to
   the training data if it happens at scale. What would you change to reduce it:
   a bigger model, a smaller one, a custom rule, or a manual review step?
3. **Add a recognizer:** add a third custom recognizer for one identifier shape
   from your own world. A good candidate is an Indian PAN card number, which has
   the shape five letters, four digits, one letter (for example ABCDE1234F). Write
   the pattern, add it to the script, and test it on a sentence of your own. Record
   whether it fired, and whether anything else fired on the same span.
4. **The standard:** write one paragraph stating your scrub standard for this course:
   what recall you require, how you will measure it, and what you will do when the
   measurement falls short. That paragraph is the beginning of your data minimization
   evidence under GDPR Article 5(1)(c).

## 9. Exercise C: Train the tokenizer and break it (20 minutes)

Run `bpe_tokenizer.py` and read `tokenizer_report.md`. Then answer these in
`findings.md`:

1. **Merges:** the first merges are end-of-word pairs and "th". By merge 25 the
   tokenizer has learned whole words ("was", "they", "all"). Why do the earliest
   merges look like letter pairs and the later ones look like words? What does that
   say about what BPE is actually learning?
2. **Compression:** the test sentences took 2.29 tokens per word. Train with 500
   merges instead of 100 (change NUM_MERGES) and re-run. What happens to tokens per
   word, and to the vocabulary size? Why does the gain flatten as merges grow?
3. **Break it:** encode a sentence with numbers, punctuation, and a word from
   another language, for example "Call me at 98765 43210, dhanyavaad!" What does the
   tokenizer do with the digits and the Hindi word? What does that tell you about a
   tokenizer trained only on simple English stories?
4. **Round trip:** all three test sentences decoded back exactly. Try a sentence
   with a capital letter in the middle, for example "McDonald ate a burger." Does
   it round-trip? Why or why not? (Hint: look at what the script does to case
   before encoding.)

## 10. What to push to GitHub

In `course/chapter-03/`:
- `README.md`: this file.
- `dedup.py`: the MinHash dedup script (already here; run it).
- `pii_scrub.py`: the Presidio scrub and recall measurement (already here; run it).
- `bpe_tokenizer.py`: the BPE trainer (already here; run it).
- `dedup_report.md`, `scrub_report.md`, `tokenizer_report.md`: the script outputs.
- `findings.md`: your answers: the four Exercise A questions, the four Exercise B
  questions, and the four Exercise C questions.

## 11. Check yourself

1. What is a shingle, and why does Jaccard similarity use sets of shingles instead
   of comparing raw text?
2. Why does MinHash estimate Jaccard instead of computing it, and what do more hash
   functions buy you?
3. What is the difference between recall and precision for a PII scrubber, and why
   can a scrubber have perfect recall and still be bad?
4. Why is an indirect identifier (age plus role plus city) hard for a detector that
   looks at one entity at a time?
5. What does BPE do with a word it has never seen, and why does that matter for
   training?

## 12. Paper seed

Your three reports are the seed of a methods paper: "Cleaning at toy scale: measuring
what dedup, PII scrubbing, and tokenization actually do to a training set." The
contribution is the measurement, not the tools: a MinHash threshold analysis with
estimated versus exact Jaccard, a Presidio recall study with wrong-type and
false-positive counts on non-US identifier shapes, and a BPE compression curve as
merges grow. Keep the reports, the scripts, and the thresholds. Chapter 15 turns
your best lab into a paper, and a paper that reports what the tools got wrong is
stronger than one that reports only that they ran.

## Key terms (first-use glossary)

- **Shingle:** a short overlapping sequence of words (here, 5 words) used to represent
  a document as a set.
- **Jaccard similarity:** the size of the overlap of two sets divided by the size of
  their union. 1.0 means identical, 0 means nothing shared.
- **MinHash:** a technique that replaces a large set with a short signature of minimum
  hash values, so similarity can be estimated without comparing the full sets.
- **LSH banding:** Locality Sensitive Hashing: grouping MinHash signatures into bands
  so only stories that share a band are compared, which makes dedup feasible at scale.
- **Recall:** of all the things that should have been found, the fraction that were
  found. For a scrubber, the fraction of personal data actually removed.
- **Precision:** of all the things found, the fraction that were correct. For a
  scrubber, the fraction of removals that were actually personal data.
- **Indirect identifier:** information that identifies a person only in combination
  with other facts, such as age plus role plus city.
- **Token:** the unit a model reads: an integer id from a fixed vocabulary. Text is
  converted to tokens before training.
- **BPE (Byte Pair Encoding):** a tokenization algorithm that starts with single
  characters and repeatedly merges the most frequent adjacent pair.
- **Vocabulary:** the fixed set of tokens a tokenizer can produce, each with its own id.
