# Privacy, Regulation & AI Safety — A 15-Chapter Practical Course

**For:** Vivek Kumar Agarwal. **Repo:** https://github.com/vagarwal89/ai-safety-research
**Focus:** the intersection of regulation, privacy, and AI safety — learned by building, not by reading.
**Level:** beginner-friendly. No prior ML engineering assumed. Every chapter explains each term once,
then gives you code to run, mostly on free Google Colab (T4 GPU).

## The spine

One pipeline: **Data → Model → Deployment → People**. Every regulation attaches at a stage.
One loop: **Govern-wrapped Map, Measure, Manage** (NIST AI RMF shape).
- Map discovers and classifies. Measure tests and monitors. Manage controls and remediates.
- Govern holds the owners, the rationale, and the evidence.
- Every lab produces evidence. Evidence is what turns a lab into a paper.

## The chapters

| # | Chapter | Core question | Lab artifact |
|---|---------|---------------|--------------|
| 1 | One System: Regulation, Privacy, and AI Safety | How do the rules fit together? | System inventory + first PII scan |
| 2 | Training Data Governance | Who owns the data, and may you use it? | Dataset datasheet + license audit |
| 3 | Data Prep That Holds Up | How do you clean data without breaking it? | MinHash dedup + PII scrub + BPE tokenizer |
| 4 | Differential Privacy, Hands On | How much privacy does noise actually buy? | Laplace mechanism + budget accounting |
| 5 | Pre-training at Toy Scale | What really happens when a model trains? | nanoGPT on TinyStories + loss curves |
| 6 | Memorization and Extraction | Can your model leak its training data? | Extraction probe on your own model |
| 7 | SFT: Teaching a Model to Assist | How does a base model become an assistant? | QLoRA SFT + instruction-following rubric |
| 8 | RLHF and DPO | How do human preferences become behavior? | Reward model + DPO + reward-hacking gallery |
| 9 | Evals That Mean Something | How do labs actually test a model? | Harness runs + custom 50-prompt safety eval |
| 10 | Red-Teaming | How do you break a model systematically? | Red-team harness + mini safety report |
| 11 | RAG as an Attack Surface | What happens when retrieval is the weak link? | RAG build, injection attack, defense |
| 12 | Fairness Testing With Teeth | How do you test bias without breaking the law? | Segregated fairness-testing pipeline (EU AI Act Art. 10 vs GDPR Art. 9) |
| 13 | Privacy-Preserving ML at Scale | How do you train without seeing the data? | DP-SGD with Opacus + privacy accounting |
| 14 | Governance in Practice | How do you decide a model is safe to ship? | Safety case + release-gate checklist |
| 15 | From Labs to a Paper | How does this become publishable research? | Paper outline + reproducibility package |

## Rules

1. Every claim about how models work must trace to something you ran.
2. Every chapter ends with a GitHub artifact and a 3-line version: what you did, what you found, why it matters.
3. Dangerous-capability content stays conceptual and defensive: evals, not enablement.
4. Keep every finding. Your best lab becomes your first paper (Chapter 15).

## Daily cadence

One chapter a day, Nov 14–29, 2026. Each day's lesson is pasted in the AI Safety Study Hub
and pushed here under `course/chapter-NN/`. Chapter 1 is live now.

## Publication path (the long game)

Candidate venues for this work: FAccT, AIES, NeurIPS Datasets & Benchmarks track, IEEE S&P,
PETS (privacy), SOUPS (usable privacy), and workshops on evals and red-teaming. Chapter 15
covers how to pick a venue, structure the paper, and build the reproducibility package.
