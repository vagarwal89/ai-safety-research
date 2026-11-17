# Chapter 4: Differential Privacy, Hands On

**Time:** ~90 minutes. **Needs:** a browser (Google Colab), nothing installed locally.
Pure Python, standard library only.
**You will finish with:** a working Laplace mechanism you wrote yourself, a
measured epsilon-versus-error curve, and a privacy budget ledger that refuses
queries when the budget is gone. You will be able to say, in numbers, how much
privacy a given amount of noise actually buys.

**Builds on Chapter 3:** the PII scrub removed 16 of 16 expected spans, but two
of them were removed for the wrong reason, and the age-plus-role-plus-city
combination was only broken up by accident. A scrubber is a heuristic: it finds
what it recognizes. Differential privacy is different in kind: it is a
mathematical guarantee that holds whether or not the attacker is clever, and
it comes with a number, epsilon, that you can audit. This chapter is the
Measure phase applied to privacy itself. It feeds Chapter 6 (you will test
whether a model trained on noised data still leaks), Chapter 12 (fairness
testing needs special-category data, and noise is one of the safeguards that
makes that lawful), and Chapter 13 (DP-SGD, where the same ideas scale up to
training).

---

## 1. The one picture: a promise you can check

Chapters 1 to 3 protected privacy by removing things: delete the names, delete
the duplicates, delete the copies. That approach has a ceiling. You can never
prove you found everything, because the next identifier shape is one you have
not thought of yet. Chapter 3 proved that point: the card ending was caught
only because it looked like a date.

Differential privacy flips the approach. Instead of promising "we removed all
the personal data," it promises this: **whether or not one particular person
is in the dataset, the published result looks almost the same.** If the result
barely changes when you add or remove one person, then the result cannot reveal
much about that person. And "almost the same" is not a feeling. It is a number:
epsilon.

```
ONE PERSON IN OR OUT  ->  RESULT CHANGES BY AT MOST A FACTOR OF e^epsilon
```

Small epsilon means the result barely moves, so the person is well protected,
but the result is noisy. Large epsilon means the result is accurate, and the
person is barely protected. The whole chapter is learning to price that trade.

## 2. The definition, in plain words

### Neighboring datasets

Two datasets are **neighboring** if they differ in exactly one person's record:
one has the person, the other does not, or one has the person's answer flipped.
Everything in differential privacy is defined on pairs of neighbors, because
"one person's data" is the unit of protection.

### Epsilon-differential privacy

A randomized procedure M satisfies **epsilon-differential privacy** (epsilon-DP,
Dwork et al., 2006) if, for every pair of neighboring datasets D and D', and
for every possible output, the probability of seeing that output from D is at
most e^epsilon times the probability of seeing it from D'. In symbols:

```
Pr[M(D) = output] <= e^epsilon * Pr[M(D') = output]
```

Read it as a limit on what an attacker can learn. Before seeing the output,
the attacker has some odds on whether you are in the data. After seeing it,
those odds can shift by at most a factor of e^epsilon. Epsilon 0 would mean
the output tells the attacker nothing at all, and is also useless, because an
output that does not depend on the data cannot say anything about it. Epsilon
infinity would mean the raw data is published as-is.

### What the numbers mean

| epsilon | max odds factor e^epsilon | plain meaning |
|---|---|---|
| 0.1 | 1.11 | strong privacy: the odds shift by about 10% |
| 0.5 | 1.65 | a typical textbook choice |
| 1.0 | 2.72 | a typical textbook and deployment choice |
| 2.0 | 7.39 | weak privacy: the odds more than double |
| 5.0 | 148.41 | almost no privacy left |
| 19.61 | about 328 million | the 2020 US Census redistricting budget, for the whole product |

The Census number needs its context, or it will mislead you. Epsilon 19.61 was
the total budget for the entire redistricting data product, spread across more
than 150 billion statistics, not the budget for one query. Per query, the
epsilon was tiny. A total budget is only meaningful next to the number of
queries it covers, which is exactly why this chapter teaches budget accounting.
The Census Bureau published the number, and researchers argued about it in
public. That argument is the model: a privacy claim you can argue about in
numbers is a real claim. A privacy claim with no number is a slogan.

### Delta: the small print

Pure epsilon-DP is strict. Real deployments often use **(epsilon, delta)-DP**,
which allows the guarantee to fail with probability at most delta. Delta is
usually set far below 1/n, where n is the number of people in the data: for
1,000 people, delta 1e-5 means the failure chance is one in 100,000. Delta is
not a second epsilon. It is a failure probability, and it is what advanced
composition charges you (section 5).

## 3. Sensitivity: the one number that decides the noise

Before you can add noise, you have to answer one question: how much can one
person change the answer? That number is the **sensitivity** of the query.
Formally, the **global sensitivity** of a function f is the largest change in
f between any two neighboring datasets.

Two cases from the lab, measured on 1,000 fictional residents:

- **Counting query** ("how many residents borrowed a book?"): one person
  flipping their answer changes the count by exactly 1. Sensitivity is 1.
- **Average query** ("what share borrowed a book?"): one person flipping
  their answer changes the average by 1/1000 = 0.001. Sensitivity is 0.001.

That factor of 1,000 is the most useful fact in this chapter. Averages over
large groups need 1,000 times less noise than counts, for the same epsilon.
That is why differential privacy works in practice: the questions worth
publishing are usually averages over many people, and those are exactly the
questions that need the least noise. A query about one person, like "did Vivek
borrow a book?", has sensitivity 1 on a 0-to-1 scale, and no amount of clever
noise makes it both private and accurate. Differential privacy protects
statistics, not individual answers. If your question is about one person, the
answer is: do not publish it.

## 4. The Laplace mechanism

### The distribution

The **Laplace distribution** is a peaked, two-sided exponential curve: most
draws land near zero, and large draws get rarer exponentially fast. Its scale
parameter b sets the width. Two facts about it matter here:

- The average size of a draw (the expected absolute value) is exactly b.
- The standard deviation is b times the square root of 2, about 1.41 * b.

### The mechanism

The **Laplace mechanism** (Dwork et al., 2006) answers a numeric query by
adding Laplace noise with scale b = sensitivity / epsilon. That one line is
the whole mechanism, and the theorem behind it is that this noise is exactly
enough to guarantee epsilon-DP for that query. Smaller epsilon means a bigger
b, which means more noise, which means more privacy and less accuracy. The
mechanism is a knob, and epsilon is the hand on it.

### What this run measured (November 17, 2026)

`laplace.py` ran the counting query ("how many of 1,000 fictional residents
borrowed a book?", true answer 451) 2,000 times at each epsilon, with noise
scale b = 1 / epsilon. The empirical errors land on top of the theory, which
is how you know the sampler is correct:

| epsilon | noise scale b | mean abs error | theory E\|noise\| | share within +/-5 |
|---|---|---|---|---|
| 0.1 | 10.00 | 9.95 | 10.00 | 42.9% |
| 0.5 | 2.00 | 2.00 | 2.00 | 93.2% |
| 1.0 | 1.00 | 0.95 | 1.00 | 99.8% |
| 2.0 | 0.50 | 0.43 | 0.50 | 100.0% |
| 5.0 | 0.20 | 0.08 | 0.20 | 100.0% |

Two details are worth noticing. First, at epsilon 0.1 the typical error is
about 10 people on a count of 451: about a 2% error for strong privacy. That
is a usable statistic. Second, at epsilon 5.0 the measured error (0.08) is
smaller than the theory (0.20). That is not a bug in the sampler: the script
rounds the noisy count to an integer, and when the noise scale is under half
a person, most noise rounds away to zero. Rounding is post-processing, and
post-processing can only help accuracy. It never costs privacy (section 5).

The average query tells the same story more sharply. Asking for the share of
borrowers (true value 45.1%) at epsilon 1.0 gives a mean absolute error of
0.10 percentage points, against a theory value of 0.10. The average is off by
a tenth of a percentage point, at an epsilon that would make a count query
off by about one person. Same data, same epsilon, far better accuracy, because
the sensitivity is 1,000 times smaller. When you design a release, prefer
averages and rates over raw counts.

## 5. Composition, post-processing, and the budget ledger

One query is easy. Real releases ask many queries, and every query spends
privacy. **Composition** is the set of rules for adding up what many queries
cost together. There are three rules you need, plus one freebie.

### Basic composition: epsilons add

If you run k queries with epsilons e1 through ek, the whole release is
(e1 + ... + ek)-DP. Ten counting queries at epsilon 0.1 cost 1.0 in total.
`budget.py` ran exactly that against a budget of 1.0, spent all of it, and
then refused the eleventh query. The refusal is the feature: without a ledger,
the eleventh query would silently push the total to 1.1 and the published
guarantee would be wrong. A statistic published without its total epsilon is
an un-auditable claim, because nobody can check what it cost.

### Advanced composition: the square root discount

When you run many queries with small epsilons each, basic composition
overcharges you. **Advanced composition** (Dwork et al., 2010) says k queries
at epsilon each compose to roughly sqrt(2 * k * ln(1/delta)) * epsilon, plus a
small correction term, at the price of a tiny failure probability delta. The
total grows like the square root of the number of queries instead of linearly.

`budget.py` computed both, and the comparison is the lesson:

| scenario | basic total | advanced total |
|---|---|---|
| 100 queries at epsilon 0.01, delta 1e-5 | 1.00 | 0.49 |
| 10 queries at epsilon 0.1, delta 1e-5 | 1.00 | 1.62 |

Advanced composition roughly halves the bill when queries are many and small,
and it loses when they are few and large. Never apply a formula blindly:
compute both and take the smaller total. That is also why real deployments
track budgets with an accountant library rather than by hand.

### Parallel composition: disjoint groups are free

If your queries touch disjoint groups of people, the total cost is the largest
epsilon, not the sum. Three counting queries, one per age band, at epsilon 0.5
each, cost 0.5 in total, because no person appears in more than one band.
Splitting a release across disjoint groups is free privacy, and it is one
reason the Census publishes per-geography counts: the geographies are
disjoint, so the budget stretches further.

### Post-processing: free, and it cannot leak

Anything you compute from an epsilon-DP output is still epsilon-DP. Rounding,
clamping a count into [0, 1000], taking an average of two noisy counts, or
plotting a chart: all free, all safe. The reason is simple: post-processing
only touches the noisy output, never the raw data, so it cannot add
information about any one person. That is why the Laplace script rounds and
clamps without spending extra budget.

### Group privacy: protecting a household costs more

Epsilon-DP for one person implies k*epsilon-DP for a group of k people. At
epsilon 1.0 per person, a household of 5 gets epsilon 5.0 of protection, and
a group of 10 gets 10.0. Differential privacy protects individuals. If your
threat model includes households or families, budget for it, or say plainly
that the guarantee is per person only.

## 6. The regulation hook: GDPR and the EU AI Act

### GDPR, Article 5(1)(c): data minimization

Article 5(1)(c) requires personal data to be adequate, relevant, and limited
to what is necessary for the purpose. A differentially private release is data
minimization in its strongest form: you publish a statistic, not the data, and
the statistic is provably limited in what it reveals about any one person.
Where Chapter 3's scrub minimized by deleting, this chapter minimizes by
bounding what can be learned. The scrub's evidence was a recall number; the
mechanism's evidence is epsilon. Both belong in the record, and epsilon is the
one a regulator can verify without trusting your detector.

### GDPR, Article 25: data protection by design and by default

Article 25 requires protection to be built into the processing, not bolted on
afterward. Choosing the query, the sensitivity, and the epsilon before you
touch the data is the design step. The budget ledger is the default step: a
system that refuses the eleventh query is protection by default, because the
safe behavior is what happens when nobody is watching.

### GDPR, Article 32 and Recital 26: security, and the anonymization question

Article 32(1) requires appropriate technical measures for the security of
processing, and names pseudonymization and encryption as examples. Differential
privacy is not named in the article, but it is widely treated as a
state-of-the-art technical measure in that sense. Be careful with the stronger
claim. Recital 26 says data that has been rendered anonymous, so the person is
not or no longer identifiable, falls outside GDPR altogether. A differentially
private statistic can support an argument that the output is anonymous, but
no regulator has set a single epsilon threshold that makes output
automatically anonymous, and whether an output counts as anonymous depends on
the full context: the epsilon, the queries, the auxiliary data an attacker
might hold, and the size of the population. The honest statement is: DP gives
you a number to put in your anonymization assessment, and a small epsilon with
a documented budget is a strong argument. It does not give you a stamp that
says "anonymous." If a vendor tells you their DP output is automatically
outside GDPR, ask for their assessment, not their slogan.

### GDPR, Article 35: the DPIA is where epsilon lives

Where processing is likely to result in high risk, Article 35 requires a Data
Protection Impact Assessment. The epsilon choice is a risk decision, and the
DPIA is where it belongs: the queries you will run, the total budget, the
composition rule you used, the delta if any, and the accuracy you accept in
return. Exercise C writes that paragraph. A DPIA that says "we use
differential privacy" without an epsilon is like a safety case that says "we
tested the model" without naming the eval.

### EU AI Act, Article 10(2)(c) and (g): preparation and mitigation

Article 10(2)(c) lists data preparation operations, and a noise step applied
to training or evaluation statistics is one such operation, recorded with its
parameters like any other cleaning step in Chapter 3. Article 10(2)(g)
requires measures to detect, prevent, and mitigate biases found in the data.
Noise is a mitigation measure of a different kind: it mitigates the risk that
training or evaluation data leaks through published statistics. And Article
10(5), the narrow door for processing special-category data for bias detection
and correction, requires safeguards. Noise applied to the fairness statistics
is one candidate safeguard, and Chapter 12 works through that pipeline in
full. None of this makes differential privacy mandatory under the Act. It
makes it one of the few mitigations whose strength you can state as a number,
which is why it keeps appearing in safety cases.

## 7. Lab setup (5 minutes)

Run this in Colab. There is nothing to install: both scripts use only the
Python standard library.

1. Open https://colab.research.google.com and start a new notebook.
2. Upload `laplace.py` and `budget.py` from this folder, or paste each one
   into a cell.
3. Run them:
   ```python
   !python laplace.py
   !python budget.py
   ```
4. Each script writes a report in the same folder: `laplace_report.md` and
   `budget_report.md`. Both scripts use fixed seeds, so your numbers will
   match the reports exactly. Change a seed or an epsilon list and re-run to
   see what moves.

## 8. Exercise A: Run the Laplace mechanism and read the trade (25 minutes)

Run `laplace.py` and read `laplace_report.md`. Then answer these in
`findings.md`:

1. **Sensitivity:** the counting query has sensitivity 1 and the average has
   sensitivity 0.001 on this data. Explain in your own words why one person's
   record moves the count by 1 but the average by only 1/1000. What would the
   sensitivity of the average be if the dataset had 10 people instead of
   1,000?
2. **The trade:** at epsilon 0.1 the typical error is about 10 people on a
   count of 451, and 42.9% of trials land within 5 of the truth. At epsilon
   1.0 the typical error is about 1 person and 99.8% land within 5. Which
   epsilon would you pick for publishing the count, and what is the cost of
   your choice in plain words: what does an attacker learn at your epsilon,
   and what accuracy do you give up?
3. **Rounding:** at epsilon 5.0 the measured error (0.08) is smaller than the
   theory (0.20). Explain why rounding to an integer shrinks the observed
   error when the noise scale is under half a person. Does rounding change
   the privacy guarantee? Why or why not?
4. **Averages:** the average query at epsilon 1.0 is off by 0.10 percentage
   points. Rewrite the same question as a count query at the same epsilon:
   how large is the error then, and why is the average the better question
   to publish?

## 9. Exercise B: Run the budget ledger and break it honestly (25 minutes)

Run `budget.py` and read `budget_report.md`. Then answer these in
`findings.md`:

1. **Refusal:** the accountant refused the eleventh query at epsilon 0.1
   against a budget of 1.0. What would the total have been if it had allowed
   it, and why does that matter for a published guarantee? Who should set the
   total budget in a real deployment: the analyst running queries, or someone
   else?
2. **Advanced composition:** it halves the bill for 100 queries at epsilon
   0.01 (0.49 vs 1.00) and loses for 10 queries at epsilon 0.1 (1.62 vs
   1.00). Explain in one paragraph why the square-root discount only pays off
   when each epsilon is small and there are many queries. Then compute both
   totals for 50 queries at epsilon 0.02 with delta 1e-5, and say which rule
   you would use. (Hint: change the numbers in `scenario_advanced` and
   re-run, or compute the formula by hand.)
3. **Parallel composition:** three age-band queries at epsilon 0.5 cost 0.5
   in total, not 1.5. Now suppose one resident appears in two bands because
   of a data error. What is the true total cost, and what does that say about
   the assumption parallel composition depends on?
4. **Group privacy:** at epsilon 1.0 per person, a household of 5 gets
   epsilon 5.0. Your Chapter 1 inventory includes a customer-service chatbot
   whose logs contain whole households. Write one paragraph: is epsilon 1.0
   per person enough for that system, or do you need to budget for households?
   What epsilon would you set if households are in scope?

## 10. Exercise C: Design a release budget for the chatbot (20 minutes)

Take the Chapter 1 customer-service chatbot and design the statistics release
you would publish about its users: for example, the share of chats about
billing, the average resolution time, and the share of chats per age band.

1. List five queries you would publish. For each, write the query, its
   sensitivity, and the epsilon you would spend on it.
2. Add up the total with basic composition. Is it inside a total budget of
   1.0? If not, which queries do you cut, and which do you move to parallel
   composition across disjoint groups?
3. Write the DPIA paragraph for this release: the total epsilon, the
   composition rule, the delta if any, the accuracy you expect at that
   epsilon, and the residual risk you accept. Keep it under 150 words. That
   paragraph is the beginning of your Article 35 evidence.
4. One query you must not publish: name a statistic about a single user or a
   group smaller than 10 people, and explain why no epsilon makes it safe to
   publish. (Hint: sensitivity does not shrink with group size the way you
   want it to.)

## 11. What to push to GitHub

In `course/chapter-04/`:
- `README.md`: this file.
- `laplace.py`: the Laplace mechanism and epsilon sweep (already here; run it).
- `budget.py`: the privacy accountant and composition scenarios (already here; run it).
- `laplace_report.md`, `budget_report.md`: the script outputs.
- `findings.md`: your answers: the four Exercise A questions, the four
  Exercise B questions, and the four Exercise C questions.

## 12. Check yourself

1. What does epsilon bound, in plain words, and what does epsilon 0 mean?
2. What is sensitivity, and why does an average over 1,000 people need 1,000
   times less noise than a count for the same epsilon?
3. Why is the noise scale sensitivity divided by epsilon, and not the other
   way around?
4. What is the difference between basic and advanced composition, and when
   does advanced composition lose?
5. Why does parallel composition cost only the largest epsilon, and what
   assumption does it depend on?
6. Why does rounding and clamping a noisy answer cost no extra budget?
7. Why is a differentially private statistic not automatically anonymous
   under GDPR, and what would you need to show?

## 13. Paper seed

Your two reports are the seed of a methods paper: "Pricing privacy at toy
scale: measuring the epsilon-accuracy trade and the cost of composition."
The contribution is the measurement, not the mechanism: an empirical
epsilon-error curve with theory comparison across five epsilons, a worked
case where advanced composition loses, and a parallel-composition design
that makes a five-query release fit inside a total budget of 1.0. The Census
comparison anchors the scale: a total budget of 19.61 across an entire
national product, against your budget of 1.0 for five queries. Keep the
reports, the scripts, and the seeds. Chapter 15 turns your best lab into a
paper, and a paper that shows where the standard formulas lose is stronger
than one that reports only that they ran.

## Key terms (first-use glossary)

- **Differential privacy:** a guarantee that the published result looks
  almost the same whether or not any one person is in the data.
- **Neighboring datasets:** two datasets that differ in exactly one person's
  record.
- **Epsilon:** the privacy parameter. It bounds how much the odds about one
  person can shift when the output is seen. Smaller means more privacy and
  more noise.
- **Privacy budget:** the total epsilon you allow yourself to spend across
  all queries on a dataset. Every query spends some of it.
- **Sensitivity:** how much one person's record can change the answer to a
  query. Global sensitivity is the largest such change over any pair of
  neighboring datasets.
- **Laplace distribution:** a peaked, two-sided exponential distribution
  used to draw noise. Its scale parameter b sets the width; the average
  absolute draw is b and the standard deviation is b times sqrt(2).
- **Laplace mechanism:** answering a numeric query by adding Laplace noise
  with scale sensitivity / epsilon. The noise is exactly enough to
  guarantee epsilon-DP.
- **Composition:** the rules for adding up the privacy cost of many
  queries. Basic composition adds the epsilons. Advanced composition grows
  like the square root of the number of queries, at the price of a small
  delta. Parallel composition costs only the largest epsilon when queries
  touch disjoint groups.
- **Delta:** in (epsilon, delta)-DP, the probability, at most delta, that
  the epsilon guarantee fails. Usually set far below 1/n for n people.
- **Post-processing:** anything computed from an already private output.
  It costs no extra budget and cannot leak, because it never touches the
  raw data.
- **Group privacy:** the fact that epsilon-DP for one person implies
  k*epsilon-DP for a group of k people.
- **Anonymization:** under GDPR Recital 26, rendering data so the person is
  not or no longer identifiable, which takes the data outside GDPR. A small
  epsilon supports that argument; no epsilon makes it automatic.
- **DPIA (Data Protection Impact Assessment):** the GDPR Article 35
  assessment for high-risk processing, where the epsilon choice and the
  budget belong.
