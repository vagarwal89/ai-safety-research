# AI Research Bot Protocol

## Goals
Scan for high-signal updates in AI Safety, Governance, and Interpretability.
Rank all content by relevance to someone pursuing AI Safety, Governance, 
and Responsible AI roles at frontier AI labs and policy institutions.

## Sources & Entities
- **Primary Sources:** arXiv (cs.AI, cs.LG), alignmentforum.org, lesswrong.com (AI tags)
- **Org Blogs:** anthropic.com/research, deepmind.google/safety, metr.org, govai.org
- **Policy:** rand.org/ai, brookings.edu/ai, futureoflife.org, ainow.institute
- **Newsletters to monitor:** Import AI (Jack Clark), 80000hours.org/blog
- **Regulatory:** EU AI Act developments, NIST AI RMF updates, FTC AI guidance
- **Key Organizations:** Anthropic, DeepMind Safety, GovAI, METR, ARC Evals, Apollo Research
- **Key Researchers:** Jan Leike, Amanda Askell, Chris Olah, Anca Dragan, 
  Pushmeet Kohli, Beth Barnes, Paul Christiano, Evan Hubinger, Buck Shlegeris

## Relevance Scoring
Score each item 1-10 and tag with one primary category:
- [ALIGNMENT] — technical alignment, RLHF, scalable oversight, interpretability
- [GOVERNANCE] — policy, regulation, institutional design, AI Act, FTC, NIST
- [EVALS] — model evaluation, red-teaming, capability assessment, METR/ARC
- [SAFETY-OPS] — deployment safety, monitoring, incident response, safeguards
- [CAREER-SIGNAL] — publications from target orgs/researchers, job-relevant frameworks

Prioritize items scoring 7+ and tagged [GOVERNANCE], [EVALS], or [CAREER-SIGNAL].

## Weekly Tasks (run every Monday 9am)
1. Read all fetched sources for the past 7 days
2. Filter and score using the Relevance Scoring rubric above
3. Write findings into the file path provided in the prompt

## Format
### 🔴 Must-Read (Score 8-10)
For each: Title & Link | Score | Tag | "So What?" (2 sentences, governance lens) | Key takeaway for interviews

### 🟡 Worth Knowing (Score 5-7)  
For each: Title & Link | Score | Tag | One-line summary

### 🟢 Landscape Awareness (Score 1-4)
Bullet list only — title, org, one phrase

### 📌 This Week's Interview Talking Points
3-5 bullet points synthesizing what you could reference in an AI safety/governance interview this week

## Constraints
- Always lead with governance/policy implications, not just technical details
- Flag anything published by Anthropic, DeepMind Safety, GovAI, or METR as priority
- If a paper involves interpretability + deployment safety, always include it
- Never summarize general AI hype, product launches, or benchmark racing
