# AI Safety & Governance Daily Briefing

**Date:** 2026-03-26

---

## Summary

No papers from the key researchers (Jan Leike, Amanda Askell, Chris Olah, Anca Dragan, Pushmeet Kohli, Beth Barnes) or key organizations (Anthropic, DeepMind Safety, GovAI, METR) were identified in today's arXiv feed. However, several papers with relevance to AI safety, governance, and interpretability themes were found.

---

## Relevant Papers

### 1. The Stochastic Gap: A Markovian Framework for Pre-Deployment Reliability and Oversight-Cost Auditing in Agentic Artificial Intelligence

**Link:** [arXiv:2603.24582](https://arxiv.org/abs/2603.24582)

**The "So What?":** This paper provides a formal framework for auditing agentic AI systems before deployment, directly addressing oversight costs and reliability—core concerns for AI governance. The ability to quantify when human-in-the-loop escalation is needed has immediate practical implications for safe deployment of autonomous AI agents in enterprise settings.

**Technical Core:** The authors develop a measure-theoretic Markov framework for agentic AI workflows, introducing metrics for state blind-spot mass, entropy-based human escalation gates, and expected oversight cost. Validated on a large purchase-to-pay log (251K cases), they find that state-action blind mass increases substantially when operational context is enriched, demonstrating that apparent state-level support can mask decision-level uncertainty.

**Relationship:** No direct affiliation with listed key researchers or organizations.

---

### 2. Retrieval Improvements Do Not Guarantee Better Answers: A Study of RAG for AI Policy QA

**Link:** [arXiv:2603.24580](https://arxiv.org/abs/2603.24580)

**The "So What?":** This work directly addresses AI governance tooling by evaluating RAG systems on AI policy documents. The finding that better retrieval can paradoxically lead to more confident hallucinations is a critical insight for anyone building AI-assisted policy analysis systems.

**Technical Core:** The authors study RAG performance on the AGORA corpus (947 AI policy documents) using a fine-tuned ColBERT retriever and DPO-aligned generator. They find that domain-specific fine-tuning improves retrieval metrics but does not consistently improve QA performance, and can increase hallucination confidence when relevant documents are absent.

**Relationship:** No direct affiliation with listed key researchers or organizations.

---

### 3. Claudini: Autoresearch Discovers State-of-the-Art Adversarial Attack Algorithms for LLMs

**Link:** [arXiv:2603.24511](https://arxiv.org/abs/2603.24511)

**The "So What?":** This paper demonstrates that LLM agents can autonomously discover novel adversarial attacks that outperform all existing methods—a significant finding for AI safety red-teaming. It suggests both promise (automated safety research) and risk (automated attack discovery) for the field.

**Technical Core:** Using an autoresearch pipeline powered by Claude Code, the authors show that agentic iteration starting from GCG attacks produces new white-box jailbreaking algorithms achieving up to 40% ASR on CBRN queries against safety-guarded models, and 100% ASR against Meta-SecAlign-70B on transfer attacks—far exceeding baselines.

**Relationship:** Uses Claude Code (Anthropic product) as the underlying agent, though no listed key researchers are authors.

---

### 4. No Single Metric Tells the Whole Story: A Multi-Dimensional Evaluation Framework for Uncertainty Attributions

**Link:** [arXiv:2603.24524](https://arxiv.org/abs/2603.24524)

**The "So What?":** Reliable uncertainty quantification is essential for safe AI deployment. This paper advances interpretability by providing a systematic evaluation framework for uncertainty attribution methods, helping practitioners understand when and why models are uncertain.

**Technical Core:** The authors align uncertainty attribution evaluation with the Co-12 XAI framework, implementing metrics for correctness, consistency, continuity, compactness, and a novel "conveyance" property. Experiments show gradient-based methods outperform perturbation-based approaches in consistency, while no single metric sufficiently captures attribution quality.

**Relationship:** No direct affiliation with listed key researchers or organizations.

---

### 5. Anti-I2V: Safeguarding your photos from malicious image-to-video generation

**Link:** [arXiv:2603.24570](https://arxiv.org/abs/2603.24570)

**The "So What?":** As generative video models become more capable, protecting individuals from unauthorized deepfake creation is a growing safety concern. This work provides a technical defense mechanism against malicious use of image-to-video diffusion models.

**Technical Core:** Anti-I2V introduces adversarial perturbations operating in L*a*b* and frequency domains to disrupt video diffusion models (including DiT architectures). By targeting layers capturing semantic features during denoising, the method degrades temporal coherence and generation fidelity, achieving state-of-the-art defense performance.

**Relationship:** No direct affiliation with listed key researchers or organizations.

---

## Papers from Key Researchers/Organizations

None identified in today's feed.

---

*Generated from arXiv feed dated 2026-03-26*