# Findings: Chapter 4: Differential Privacy, Hands On

Fill this in as you work. One line per question is enough, but each line must
trace to something you read or ran. The measured numbers from the November 17,
2026 run are already filled in below; your job is the reasoning.

## Measured results (November 17, 2026 run)

- Laplace mechanism, synthetic data: 1,000 fictional residents, 451 borrowed
  a book (45.1%). One person's flipped answer changes the count by 1 and the
  average by 0.001.
- Epsilon sweep, counting query, 2,000 trials each (noise scale b = 1/epsilon):
  eps 0.1: mean abs error 9.95 (theory 10.00), 42.9% within +/-5.
  eps 0.5: mean abs error 2.00 (theory 2.00), 93.2% within +/-5.
  eps 1.0: mean abs error 0.95 (theory 1.00), 99.8% within +/-5.
  eps 2.0: mean abs error 0.43 (theory 0.50), 100% within +/-5.
  eps 5.0: mean abs error 0.08 (theory 0.20), 100% within +/-5; rounding
  shrinks the observed error below theory when the noise scale is under 0.5.
- Average query at eps 1.0: mean abs error 0.1011 percentage points
  (theory 0.1000). True share 45.1%.
- Budget ledger: total budget 1.0; 10 queries at eps 0.1 spent it exactly;
  the 11th query was REFUSED.
- Advanced composition, delta 1e-5: 100 queries at eps 0.01: 0.49 vs basic
  1.00 (wins). 10 queries at eps 0.1: 1.62 vs basic 1.00 (loses).
- Parallel composition: 3 age-band queries at eps 0.5 cost 0.5 total, not 1.5.
- Group privacy at eps 1.0 per person: group of 5 gets eps 5.0; group of 10
  gets eps 10.0.
- Reference: 2020 US Census redistricting product, total epsilon 19.61
  (17.14 persons + 2.47 housing), spread across more than 150 billion
  statistics (Census Bureau, June 2021).

## Exercise A: The Laplace mechanism and the trade

1. **Sensitivity:** why does one person move the count by 1 but the average
   by only 1/1000? What is the average's sensitivity with 10 people?
   - Answer: ___
2. **The trade:** which epsilon would you pick for publishing the count, and
   what does an attacker learn at your epsilon, and what accuracy do you give up?
   - Epsilon I would pick: ___
   - Reasoning: ___
3. **Rounding:** why does rounding shrink the observed error at eps 5.0, and
   does it change the privacy guarantee?
   - Answer: ___
4. **Averages:** how large is the error if the same question is asked as a
   count at eps 1.0, and why is the average the better question to publish?
   - Answer: ___

## Exercise B: The budget ledger

1. **Refusal:** what would the total have been if the 11th query had been
   allowed, and who should set the total budget in a real deployment?
   - Answer: ___
2. **Advanced composition:** why does the square-root discount only pay off
   when each epsilon is small and there are many queries? Compute both totals
   for 50 queries at eps 0.02, delta 1e-5, and say which rule you would use.
   - Basic total: ___
   - Advanced total: ___
   - Rule I would use: ___
3. **Parallel composition:** if one resident appears in two bands because of
   a data error, what is the true total cost, and what assumption does
   parallel composition depend on?
   - Answer: ___
4. **Group privacy:** is eps 1.0 per person enough for the chatbot whose logs
   contain whole households, or do you need to budget for households?
   - Answer: ___

## Exercise C: Design a release budget for the chatbot

1. **My five queries** (query, sensitivity, epsilon each):
   - ___
   - ___
   - ___
   - ___
   - ___
2. **Total with basic composition:** ___ Is it inside a budget of 1.0? What
   did you cut or move to parallel composition?
   - Answer: ___
3. **DPIA paragraph** (under 150 words: total epsilon, composition rule,
   delta, expected accuracy, residual risk):
   - Answer: ___
4. **One query I must not publish** (a statistic about one user or a group
   smaller than 10), and why no epsilon makes it safe:
   - Answer: ___

## My privacy budget rule for this course

What total epsilon will I allow per release, how will I track it, and what
happens when a query would bust the budget?
- Answer: ___
