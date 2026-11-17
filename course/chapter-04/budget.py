#!/usr/bin/env python3
"""Chapter 4: privacy budget accounting in pure Python.

No libraries to install: only the standard library (math).
Run it with:  python budget.py
It writes budget_report.md in this folder.

What it does, in plain words:
  1. A PrivacyAccountant: a ledger that tracks how much epsilon you have
     spent, refuses a query that would push you over budget, and reports
     what is left. This is the habit every real deployment needs: privacy
     is a finite resource, and every query spends some of it.
  2. Basic composition: epsilons add. Ten queries at epsilon 0.1 cost 1.0.
  3. Advanced composition: with many small queries, the total grows like
     the square root of the number of queries instead of linearly, at the
     price of a tiny failure probability delta. It only wins when each
     query's epsilon is small; the script shows a case where it loses.
  4. Parallel composition: queries on disjoint groups of people cost only
     the largest epsilon, not the sum, because no one person appears in
     more than one query.
  5. Group privacy: protecting a group of k people costs k times the
     epsilon of protecting one person.

All numbers are computed here, not asserted: the advanced-composition
formula is evaluated directly from Dwork et al. (2010).
"""

import math
import os

# ---------------------------------------------------------------------------
# The accountant
# ---------------------------------------------------------------------------

class PrivacyAccountant:
    """A ledger for a total privacy budget.

    total_budget: the epsilon you are allowed to spend, set before any query.
    spent: epsilon used so far. Every spend() call either records the query
    or refuses it. Refusal is the point: an accountant that lets you overspend
    is not an accountant.
    """

    def __init__(self, total_budget):
        self.total_budget = total_budget
        self.spent = 0.0
        self.ledger = []

    def spend(self, epsilon, name):
        """Record one query. Returns True if allowed, False if it would bust the budget."""
        if self.spent + epsilon > self.total_budget + 1e-12:
            self.ledger.append((name, epsilon, "REFUSED"))
            return False
        self.spent += epsilon
        self.ledger.append((name, epsilon, "ok"))
        return True

    def remaining(self):
        return self.total_budget - self.spent


# ---------------------------------------------------------------------------
# Composition formulas
# ---------------------------------------------------------------------------

def basic_composition(epsilons):
    """Basic composition (Dwork et al., 2006): epsilons add."""
    return sum(epsilons)


def advanced_composition(k, eps, delta_prime):
    """Advanced composition (Dwork et al., 2010).

    k mechanisms, each eps-DP (delta 0), compose to (eps_total, delta_prime)-DP
    with eps_total = sqrt(2 * k * ln(1/delta_prime)) * eps
                     + k * eps * (e^eps - 1).
    The tiny delta_prime is the price: with probability at most delta_prime,
    the guarantee can fail. delta_prime = 1e-5 means one failure in 100,000
    runs, which is the usual scale for a dataset of this size.
    """
    term1 = math.sqrt(2 * k * math.log(1.0 / delta_prime)) * eps
    term2 = k * eps * (math.exp(eps) - 1)
    return term1 + term2


# ---------------------------------------------------------------------------
# The scenarios
# ---------------------------------------------------------------------------

def scenario_basic():
    """Ten counting queries at epsilon 0.1 each, budget 1.0."""
    acct = PrivacyAccountant(total_budget=1.0)
    for i in range(1, 11):
        acct.spend(0.1, f"count query {i}")
    eleventh = acct.spend(0.1, "count query 11 (extra)")
    return {
        "queries": 10,
        "per_query": 0.1,
        "basic_total": basic_composition([0.1] * 10),
        "spent": acct.spent,
        "remaining": acct.remaining(),
        "eleventh_allowed": eleventh,
        "ledger": acct.ledger,
    }


def scenario_advanced():
    """One hundred queries at epsilon 0.01 each: basic says 1.0, advanced says less."""
    k, eps, delta_prime = 100, 0.01, 1e-5
    return {
        "k": k,
        "eps": eps,
        "delta_prime": delta_prime,
        "basic_total": basic_composition([eps] * k),
        "advanced_total": advanced_composition(k, eps, delta_prime),
    }


def scenario_advanced_loses():
    """Ten queries at epsilon 0.1: advanced composition is WORSE than basic.

    The square-root term only pays off when each epsilon is small and k is
    large. With eps = 0.1 and k = 10, the linear term k*eps*(e^eps - 1) is
    already large, and the sqrt term is not small enough to compensate.
    """
    k, eps, delta_prime = 10, 0.1, 1e-5
    return {
        "k": k,
        "eps": eps,
        "delta_prime": delta_prime,
        "basic_total": basic_composition([eps] * k),
        "advanced_total": advanced_composition(k, eps, delta_prime),
    }


def scenario_parallel():
    """Three counting queries on three disjoint age bands, epsilon 0.5 each.

    No resident belongs to more than one band, so no one person's data is
    touched by more than one query. Parallel composition: total = max, not sum.
    """
    per_query = 0.5
    return {
        "bands": ["18-29", "30-49", "50+"],
        "per_query": per_query,
        "naive_sum": 3 * per_query,
        "parallel_total": max([per_query] * 3),
    }


def scenario_group_privacy(eps=1.0):
    """Pure epsilon-DP for one person implies k*epsilon-DP for a group of k."""
    return [(k, k * eps) for k in [1, 2, 5, 10]]


# ---------------------------------------------------------------------------
# Run everything and write the report
# ---------------------------------------------------------------------------

def main():
    basic = scenario_basic()
    adv = scenario_advanced()
    adv_loses = scenario_advanced_loses()
    par = scenario_parallel()
    groups = scenario_group_privacy(eps=1.0)

    lines = []
    lines.append("# Privacy Budget Report")
    lines.append("")
    lines.append("Generated by `budget.py` (Chapter 4). Pure Python, standard "
                 "library only. All composition totals are computed from the "
                 "formulas, not asserted.")
    lines.append("")
    lines.append("## Scenario 1: basic composition, and the accountant refusing a query")
    lines.append("")
    lines.append(f"- Total budget: epsilon {basic['spent'] + basic['remaining']:.1f}")
    lines.append(f"- Queries run: {basic['queries']} counting queries at epsilon "
                 f"{basic['per_query']} each")
    lines.append(f"- Basic composition total: {basic['basic_total']:.1f}")
    lines.append(f"- Spent: {basic['spent']:.1f}; remaining: {basic['remaining']:.1f}")
    lines.append(f"- Eleventh query at epsilon 0.1 allowed? "
                 f"{'yes' if basic['eleventh_allowed'] else 'NO, refused'}")
    lines.append("")
    lines.append("The refusal is the feature. Without an accountant, the eleventh "
                 "query would silently push the total to 1.1 and the published "
                 "guarantee would be wrong. Real deployments (the Census Bureau, "
                 "Apple, Google) track the same ledger, just with more queries.")
    lines.append("")
    lines.append("## Scenario 2: advanced composition, where it wins")
    lines.append("")
    lines.append(f"- {adv['k']} queries at epsilon {adv['eps']} each, "
                 f"delta' = {adv['delta_prime']}")
    lines.append(f"- Basic composition total: {adv['basic_total']:.2f}")
    lines.append(f"- Advanced composition total: {adv['advanced_total']:.2f} "
                 f"(with failure probability at most {adv['delta_prime']})")
    lines.append("")
    lines.append("With 100 small queries, advanced composition roughly halves the "
                 "bill: 0.49 instead of 1.0. The total grows like the square root "
                 "of the number of queries instead of linearly. The price is a "
                 "tiny delta: with probability at most 1 in 100,000 the guarantee "
                 "can fail, which is why deployments pick delta well below 1/n, "
                 "where n is the number of people in the data.")
    lines.append("")
    lines.append("## Scenario 3: advanced composition, where it loses")
    lines.append("")
    lines.append(f"- {adv_loses['k']} queries at epsilon {adv_loses['eps']} each, "
                 f"delta' = {adv_loses['delta_prime']}")
    lines.append(f"- Basic composition total: {adv_loses['basic_total']:.2f}")
    lines.append(f"- Advanced composition total: {adv_loses['advanced_total']:.2f}")
    lines.append("")
    lines.append("Here advanced composition is worse: 1.62 instead of 1.0. The "
                 "square-root term only pays off when each epsilon is small and "
                 "there are many queries. Never apply a formula blindly; compute "
                 "both and take the smaller total.")
    lines.append("")
    lines.append("## Scenario 4: parallel composition on disjoint groups")
    lines.append("")
    lines.append(f"- Three age bands: {', '.join(par['bands'])}")
    lines.append(f"- One counting query per band, epsilon {par['per_query']} each")
    lines.append(f"- Naive sum: {par['naive_sum']}")
    lines.append(f"- Parallel composition total: {par['parallel_total']}")
    lines.append("")
    lines.append("Because no person appears in more than one band, the three "
                 "queries together cost only 0.5, not 1.5. Splitting queries "
                 "across disjoint groups is free privacy. It is also the reason "
                 "the Census publishes per-geography counts: the geographies are "
                 "disjoint, so the budget stretches further.")
    lines.append("")
    lines.append("## Scenario 5: group privacy")
    lines.append("")
    lines.append("A mechanism that is epsilon-DP for one person is k*epsilon-DP "
                 "for a group of k people. At epsilon 1.0 per person:")
    lines.append("")
    lines.append("| group size k | effective epsilon for the group |")
    lines.append("|---|---|")
    for k, eff in groups:
        lines.append(f"| {k} | {eff:.1f} |")
    lines.append("")
    lines.append("A household of 5 gets epsilon 5.0 of protection from a mechanism "
                 "that gives epsilon 1.0 to an individual. Differential privacy "
                 "protects individuals; protecting groups costs proportionally more. "
                 "If your threat model includes households or families, budget for it.")
    lines.append("")
    lines.append("## The rule to take away")
    lines.append("")
    lines.append("Every query spends budget. Basic composition adds the epsilons. "
                 "Advanced composition can cut the bill when queries are many and "
                 "small, at the price of a tiny delta. Parallel composition is free "
                 "across disjoint groups. Keep a ledger, refuse queries that bust "
                 "the budget, and publish the total epsilon alongside the results: "
                 "a statistic without its epsilon is an un-auditable claim.")
    lines.append("")

    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "budget_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path}")
    print(f"Basic: 10 x 0.1 = {basic['basic_total']:.1f}; "
          f"11th query allowed: {basic['eleventh_allowed']}")
    print(f"Advanced (100 x 0.01): {adv['advanced_total']:.2f} vs basic "
          f"{adv['basic_total']:.2f}")
    print(f"Advanced (10 x 0.1): {adv_loses['advanced_total']:.2f} vs basic "
          f"{adv_loses['basic_total']:.2f}")
    print(f"Parallel (3 x 0.5 on disjoint bands): {par['parallel_total']}")


if __name__ == "__main__":
    main()
