#!/usr/bin/env python3
"""Chapter 4: the Laplace mechanism in pure Python.

No libraries to install: only the standard library (random, math, statistics).
Run it with:  python laplace.py
It writes laplace_report.md in this folder.

What it does, in plain words:
  1. Builds a small synthetic dataset: 1,000 fictional residents of a fictional
     town. Each resident has an age band and two yes/no facts: whether they
     borrowed a book this month, and whether they used the library wifi.
  2. Shows sensitivity: changing ONE person's record changes a counting query
     by at most 1, and an average over 1,000 people by at most 1/1000.
  3. Runs the Laplace mechanism: adds random noise drawn from the Laplace
     distribution, scaled by sensitivity / epsilon. Repeats the noisy count
     2,000 times at five epsilon values and measures the actual error.
  4. Shows post-processing: clamping and rounding the noisy answer costs no
     extra privacy budget.
  5. Prints the epsilon-to-odds table: what each epsilon value actually means
     for how much an attacker can learn about one person.

Everything here is synthetic and seeded, so your numbers will match the
report exactly. Change SEED or the epsilon list and re-run to see what moves.
"""

import math
import os
import random
import statistics

# ---------------------------------------------------------------------------
# The mechanism
# ---------------------------------------------------------------------------

def laplace_noise(scale, rng):
    """Draw one sample from the Laplace distribution with mean 0 and scale b.

    Uses the inverse-CDF method: take a uniform random number u in (0, 1) and
    return -b * sign(u - 0.5) * ln(1 - 2*|u - 0.5|). This is the standard way
    to sample Laplace noise without any special library.
    """
    u = rng.random()
    while u == 0.0 or u == 1.0:  # keep u strictly inside (0, 1)
        u = rng.random()
    if u < 0.5:
        return scale * math.log(2.0 * u)
    return -scale * math.log(2.0 * (1.0 - u))


def laplace_mechanism(true_value, sensitivity, epsilon, rng, low=None, high=None):
    """Return a differentially private version of true_value.

    Adds Laplace noise with scale = sensitivity / epsilon, then rounds to an
    integer and clamps into [low, high] if bounds are given. The rounding and
    clamping are post-processing: they cost no extra privacy budget, because
    differential privacy is immune to post-processing (Chapter 4, section 5).
    """
    scale = sensitivity / epsilon
    noisy = true_value + laplace_noise(scale, rng)
    noisy = round(noisy)
    if low is not None:
        noisy = max(low, noisy)
    if high is not None:
        noisy = min(high, noisy)
    return noisy


# ---------------------------------------------------------------------------
# The synthetic dataset
# ---------------------------------------------------------------------------

N = 1000
SEED = 7

def build_dataset(seed=SEED):
    """1,000 fictional residents. Nothing here is real personal data."""
    rng = random.Random(seed)
    bands = ["18-29", "30-49", "50+"]
    rows = []
    for _ in range(N):
        rows.append({
            "age_band": rng.choice(bands),
            "borrowed_book": rng.random() < 0.42,
            "used_wifi": rng.random() < 0.65,
        })
    return rows


# ---------------------------------------------------------------------------
# Experiment 1: sensitivity
# ---------------------------------------------------------------------------

def experiment_sensitivity(rows):
    true_count = sum(1 for r in rows if r["borrowed_book"])
    # Flip ONE person's answer: the worst case for a counting query.
    changed = [dict(r) for r in rows]
    changed[0]["borrowed_book"] = not changed[0]["borrowed_book"]
    changed_count = sum(1 for r in changed if r["borrowed_book"])
    count_diff = abs(true_count - changed_count)

    true_avg = true_count / N
    changed_avg = changed_count / N
    avg_diff = abs(true_avg - changed_avg)
    return {
        "true_count": true_count,
        "count_diff_one_person": count_diff,
        "true_avg": true_avg,
        "avg_diff_one_person": avg_diff,
    }


# ---------------------------------------------------------------------------
# Experiment 2: the epsilon sweep on a counting query
# ---------------------------------------------------------------------------

EPSILONS = [0.1, 0.5, 1.0, 2.0, 5.0]
TRIALS = 2000

def experiment_epsilon_sweep(true_count, sensitivity=1.0):
    rng = random.Random(123)
    rows_out = []
    for eps in EPSILONS:
        scale = sensitivity / eps
        errors = []
        within_5 = 0
        for _ in range(TRIALS):
            noisy = laplace_mechanism(true_count, sensitivity, eps, rng,
                                      low=0, high=N)
            err = noisy - true_count
            errors.append(err)
            if abs(err) <= 5:
                within_5 += 1
        abs_errors = [abs(e) for e in errors]
        rows_out.append({
            "epsilon": eps,
            "scale": scale,
            "mean_abs_error": statistics.mean(abs_errors),
            "theory_mean_abs_error": scale,          # E|noise| = b
            "empirical_std": statistics.stdev(errors),
            "theory_std": scale * math.sqrt(2),     # std of Laplace = b*sqrt(2)
            "frac_within_5": within_5 / TRIALS,
        })
    return rows_out


# ---------------------------------------------------------------------------
# Experiment 3: an average query needs far less noise
# ---------------------------------------------------------------------------

def experiment_average(true_avg, sensitivity, epsilon=1.0):
    rng = random.Random(456)
    errors = []
    for _ in range(TRIALS):
        noisy = true_avg + laplace_noise(sensitivity / epsilon, rng)
        errors.append(noisy - true_avg)
    abs_errors = [abs(e) for e in errors]
    return {
        "epsilon": epsilon,
        "sensitivity": sensitivity,
        "scale": sensitivity / epsilon,
        "mean_abs_error_points": statistics.mean(abs_errors) * 100,
        "theory_mean_abs_error_points": (sensitivity / epsilon) * 100,
    }


# ---------------------------------------------------------------------------
# Experiment 4: what epsilon means in odds
# ---------------------------------------------------------------------------

def epsilon_odds_table():
    return [(eps, math.exp(eps)) for eps in [0.1, 0.5, 1.0, 2.0, 5.0, 19.61]]


# ---------------------------------------------------------------------------
# Run everything and write the report
# ---------------------------------------------------------------------------

def main():
    rows = build_dataset()
    sens = experiment_sensitivity(rows)
    sweep = experiment_epsilon_sweep(sens["true_count"])
    avg = experiment_average(sens["true_avg"], sensitivity=1.0 / N, epsilon=1.0)
    odds = epsilon_odds_table()

    lines = []
    lines.append("# Laplace Mechanism Report")
    lines.append("")
    lines.append("Generated by `laplace.py` (Chapter 4). Pure Python, standard "
                 "library only. Synthetic dataset: 1,000 fictional residents, "
                 "seed 7. Noise trials: 2,000 per epsilon value, seeds 123 and 456.")
    lines.append("")
    lines.append("## Dataset")
    lines.append("")
    lines.append(f"- Residents: {N}")
    lines.append(f"- Borrowed a book this month: {sens['true_count']} "
                 f"({100 * sens['true_avg']:.1f}%)")
    lines.append(f"- Used the library wifi: "
                 f"{sum(1 for r in rows if r['used_wifi'])}")
    lines.append("")
    lines.append("## Experiment 1: sensitivity (one person changes the answer by how much?)")
    lines.append("")
    lines.append(f"- Counting query, true count: {sens['true_count']}")
    lines.append(f"- Flipping ONE person's answer changes the count by: "
                 f"{sens['count_diff_one_person']}")
    lines.append(f"- Same query as an average: true average "
                 f"{sens['true_avg']:.3f}")
    lines.append(f"- Flipping ONE person's answer changes the average by: "
                 f"{sens['avg_diff_one_person']:.4f} (sensitivity 1/{N} = 0.001)")
    lines.append("")
    lines.append("Sensitivity is the whole game: a count has sensitivity 1, an "
                 "average over 1,000 people has sensitivity 0.001, so the average "
                 "needs 1,000 times less noise for the same epsilon.")
    lines.append("")
    lines.append("## Experiment 2: epsilon sweep on the counting query")
    lines.append("")
    lines.append("Noise scale b = sensitivity / epsilon. Theory: mean absolute "
                 "error = b, standard deviation = b * sqrt(2).")
    lines.append("")
    lines.append("| epsilon | noise scale b | mean abs error | theory E|noise| | "
                 "empirical std | theory std | share within +/-5 |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in sweep:
        lines.append(f"| {r['epsilon']} | {r['scale']:.2f} | "
                     f"{r['mean_abs_error']:.2f} | {r['theory_mean_abs_error']:.2f} | "
                     f"{r['empirical_std']:.2f} | {r['theory_std']:.2f} | "
                     f"{r['frac_within_5']:.1%} |")
    lines.append("")
    lines.append("Read it as a trade: epsilon 0.1 gives strong privacy and a "
                 "typical error of about 10 people on a count of a few hundred. "
                 "Epsilon 5.0 gives a typical error under 1 person, and almost "
                 "no privacy. The empirical numbers land on top of the theory, "
                 "which is how you know the sampler is correct.")
    lines.append("")
    lines.append("## Experiment 3: the same data as an average query")
    lines.append("")
    lines.append(f"- Query: share of residents who borrowed a book, "
                 f"true value {sens['true_avg']:.1%}")
    lines.append(f"- Sensitivity: {avg['sensitivity']} (1/{N})")
    lines.append(f"- Epsilon: {avg['epsilon']}")
    lines.append(f"- Noise scale: {avg['scale']}")
    lines.append(f"- Mean absolute error: {avg['mean_abs_error_points']:.4f} "
                 f"percentage points (theory "
                 f"{avg['theory_mean_abs_error_points']:.4f})")
    lines.append("")
    lines.append("At epsilon 1.0 the average is off by about a tenth of a "
                 "percentage point. Averages over large groups are where "
                 "differential privacy is nearly free, and that is why real "
                 "deployments publish statistics, not raw rows.")
    lines.append("")
    lines.append("## Experiment 4: what epsilon means in odds")
    lines.append("")
    lines.append("Epsilon bounds the odds ratio: seeing the output can shift the "
                 "odds that a given person is in the data by at most a factor of "
                 "e^epsilon.")
    lines.append("")
    lines.append("| epsilon | max odds factor e^epsilon | plain meaning |")
    lines.append("|---|---|---|")
    for eps, factor in odds:
        if eps == 19.61:
            meaning = "2020 US Census redistricting budget (whole product)"
        elif eps <= 0.1:
            meaning = "strong privacy: odds shift by about 10%"
        elif eps <= 1.0:
            meaning = "typical textbook / deployment choice"
        else:
            meaning = "weak privacy: odds more than double"
        lines.append(f"| {eps} | {factor:.2f} | {meaning} |")
    lines.append("")
    lines.append("## Post-processing note")
    lines.append("")
    lines.append("Every noisy count above was rounded to an integer and clamped "
                 "into [0, 1000]. That costs no extra budget: anything you compute "
                 "from an epsilon-DP output is still epsilon-DP. Clamping cannot "
                 "leak, because it only uses the noisy output, never the raw data.")
    lines.append("")

    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "laplace_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path}")
    print(f"True count: {sens['true_count']}; one-person change: "
          f"{sens['count_diff_one_person']}")
    for r in sweep:
        print(f"eps={r['epsilon']}: mean abs error {r['mean_abs_error']:.2f} "
              f"(theory {r['theory_mean_abs_error']:.2f}), "
              f"within +/-5: {r['frac_within_5']:.1%}")
    print(f"Average query at eps=1.0: mean abs error "
          f"{avg['mean_abs_error_points']:.4f} percentage points")


if __name__ == "__main__":
    main()
