# AI Research Bot Protocol

## Goals
Scan for high-signal updates in AI Safety, Governance, and Interpretability.

## Sources & Entities
- **Primary Sources:** arXiv (cs.AI, cs.LG), alignmentforum.org
- **Key Organizations:** Anthropic, DeepMind Safety, GovAI, METR
- **Key Researchers:** Jan Leike, Amanda Askell, Chris Olah, Anca Dragan, Pushmeet Kohli, Beth Barnes

## Daily Tasks
1. **Read** reports/arxiv_raw.xml which contains today's latest arXiv papers in XML format.
2. **Filter:** Prioritize any paper related to the "Key Researchers" or "Key Organizations" listed above.
3. **Summarize:** Write your findings into the file path provided in the prompt.
4. **Format:** For each relevant paper, provide:
   - **Title & Link**
   - **The "So What?":** 2 sentences on why this matters for safety/governance.
   - **Technical Core:** A brief summary of the abstract.
   - **Relationship:** Mention if it relates to any of the key researchers or organizations.

## Constraints
- If no high-signal papers are found, write "No critical updates today." into the file.
- Do not summarize general "hype" or marketing-heavy AI news.
- Always write content to the file — never leave it empty.
- Use the arXiv data provided — do not rely on training knowledge for paper details.
