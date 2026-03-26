# AI Research Bot Protocol

## Goals
Scan for high-signal updates in AI Safety, Governance, and Interpretability.

## Sources & Entities
- **Primary Sources:** arXiv (cs.AI, cs.LG), alignmentforum.org
- **Key Organizations:** Anthropic, DeepMind Safety, GovAI, METR
- **Key Researchers:** Jan Leike, Amanda Askell, Chris Olah, Anca Dragan, Pushmeet Kohli, Beth Barnes

## Daily Tasks
1. **Search:** Use the arXiv API/MCP to find papers from the last 24 hours.
2. **Filter:** Prioritize any paper authored by the "Key Researchers" or "Key Organizations" listed above.
3. **Summarize:** Create a new file in the `reports/` folder named `daily-briefing-YYYY-MM-DD.md`.
4. **Format:** For each relevant paper, provide:
- **Title & Link**
- **The "So What?":** 2 sentences on why this matters for safety/governance.
- **Technical Core:** A brief summary of the abstract.
- **Relationship:** Mention if it relates to any of the key researchers.

## Constraints
- If no high-signal papers are found, create a report stating "No critical updates today."
- Do not summarize general "hype" or marketing-heavy AI news.
