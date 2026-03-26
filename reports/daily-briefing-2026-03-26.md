# AI Safety & Governance Daily Briefing
**Date:** 2026-03-26  
**File:** `reports/daily-briefing-2026-03-26.md`

---

## 🔴 Must-Read (Score 8-10)

### 1. Claudini: Autoresearch Discovers State-of-the-Art Adversarial Attack Algorithms for LLMs
**Link:** [arXiv:2603.24511](https://arxiv.org/abs/2603.24511v1)  
**Score:** 9 | **Tag:** [EVALS]

**So What?** This paper demonstrates that autonomous LLM agents can discover novel adversarial attack algorithms that outperform all 30+ existing methods, achieving 100% ASR against Meta-SecAlign-70B. This fundamentally changes the threat model for AI safety—adversarial red-teaming is now automatable, meaning defensive measures must anticipate AI-discovered attack vectors.

**Key takeaway for interviews:** "Automated red-teaming via LLM agents is no longer theoretical—Claudini achieved 100% attack success on hardened models, suggesting safety teams need continuous automated adversarial evaluation rather than static red-team exercises."

---

### 2. The Stochastic Gap: A Markovian Framework for Pre-Deployment Reliability and Oversight-Cost Auditing in Agentic AI
**Link:** [arXiv:2603.24582](https://arxiv.org/abs/2603.24582v1)  
**Score:** 9 | **Tag:** [SAFETY-OPS]

**So What?** This paper provides a formal framework for quantifying when agentic AI systems should escalate to human oversight, with concrete metrics for "blind-spot mass" in decision-making. For governance, this offers auditable, pre-deployment criteria that regulators could use to assess whether agentic systems have appropriate human-in-the-loop safeguards.

**Key takeaway for interviews:** "The paper introduces measurable oversight-cost thresholds—state-action blind mass increased from 1.6% to 12.5% when operational context was refined, demonstrating that apparent autonomy competence can mask significant edge-case vulnerability."

---

### 3. Retrieval Improvements Do Not Guarantee Better Answers: A Study of RAG for AI Policy QA
**Link:** [arXiv:2603.24580](https://arxiv.org/abs/2603.24580v1)  
**Score:** 8 | **Tag:** [GOVERNANCE]

**So What?** Using the AGORA corpus of 947 AI policy documents, researchers found that better retrieval paradoxically leads to more confident hallucinations when documents are missing from the corpus. This directly impacts AI governance tooling—policy analysts using RAG systems may receive authoritative-sounding but fabricated regulatory guidance.

**Key takeaway for interviews:** "Component-level improvements don't guarantee system-level reliability—this is a critical lesson for deploying AI tools in policy contexts where confident hallucination about regulatory requirements could have serious compliance consequences."

---

## 🟡 Worth Knowing (Score 5-7)

### 4. Anti-I2V: Safeguarding your photos from malicious image-to-video generation
**Link:** [arXiv:2603.24570](https://arxiv.org/abs/2603.24570v1)  
**Score:** 6 | **Tag:** [SAFETY-OPS]

Defensive adversarial perturbations against DiT-based video generation models; relevant to deepfake policy and content authenticity frameworks.

---

### 5. No Single Metric Tells the Whole Story: A Multi-Dimensional Evaluation Framework for Uncertainty Attributions
**Link:** [arXiv:2603.24524](https://arxiv.org/abs/2603.24524v1)  
**Score:** 6 | **Tag:** [EVALS]

Proposes Co-12-aligned evaluation framework for XAI uncertainty attributions; introduces "conveyance" metric measuring whether epistemic uncertainty propagates to feature attributions.

---

### 6. Multi-Agent Reasoning with Consistency Verification Improves Uncertainty Calibration in Medical MCQA
**Link:** [arXiv:2603.24481](https://arxiv.org/abs/2603.24481v1)  
**Score:** 6 | **Tag:** [SAFETY-OPS]

Two-phase self-verification reduces Expected Calibration Error by 49-74% in medical QA; demonstrates practical deferral signals for safety-critical deployment.

---

### 7. Towards Safe Learning-Based Non-Linear Model Predictive Control through Recurrent Neural Network Modeling
**Link:** [arXiv:2603.24503](https://arxiv.org/abs/2603.24503v1)  
**Score:** 5 | **Tag:** [SAFETY-OPS]

Safe Sequential-AMPC wraps neural policies in safety-augmented fallback mechanisms; relevant to safety constraints in learned control systems.

---

### 8. Why Does Self-Distillation (Sometimes) Degrade the Reasoning Capability of LLMs?
**Link:** [arXiv:2603.24472](https://arxiv.org/abs/2603.24472v1)  
**Score:** 5 | **Tag:** [ALIGNMENT]

Self-distillation suppresses "epistemic verbalization"—models expressing uncertainty—causing up to 40% OOD performance drops; implications for post-training safety properties.

---

## 🟢 Landscape Awareness (Score 1-4)

- **Polynomial Speedup in Diffusion Models** — Jacot — ML efficiency, no safety relevance
- **DreamerAD: Latent World Model for Autonomous Driving** — Yang et al. — robotics application
- **EndoVGGT: Surgical 3D Reconstruction** — Fan et al. — medical CV
- **Chameleon: Episodic Memory for Robotics** — Guo et al. — embodied AI
- **VFIG: Vectorizing Complex Figures** — He et al. — document processing
- **Completeness of Unbounded Best-First Minimax** — Cohen-Solal — game theory
- **Trust Region Constrained Bayesian Optimization** — Chowdhury et al. — optimization methods
- **RAVEN: EHR Foundation Model** — Rajamohan et al. — healthcare ML
- **Free-Market Algorithm** — Jaraiz — novel metaheuristic
- **LensWalk: Agentic Video Understanding** — Li et al. — video reasoning
- **Chunking Strategies for RAG** — Taiwo & Yusoff — enterprise IR
- **ASR Bias in Newcastle English** — Serditova & Tang — fairness in speech systems
- **SEGAR: Generative AR** — Bu et al. — augmented reality
- **CliPPER: Surgical Video-Language Pretraining** — Stilz et al. — medical foundation models
- **UI-Voyager: Self-Evolving GUI Agent** — Lin et al. — GUI automation
- **Incongruent Normal Form for Self-Reference** — Singh & Parmar — formal logic
- **TuneShift-KD: Knowledge Distillation** — Guan et al. — model transfer
- **AVO: Agentic Variation Operators** — Chen et al. (NVIDIA) — kernel optimization
- **Uniform Laws of Large Numbers** — Holzman et al. — statistical learning theory
- **Composer 2 Technical Report** — Cursor Research — coding model benchmark
- **Conformalized Transfer Learning for Batteries** — Filgueira da Silva et al. — engineering application
- **Divergence-Free Neural Operators** — Li et al. — physics-informed ML

---

## 📌 This Week's Interview Talking Points

1. **Automated adversarial research is here:** Claudini demonstrates that LLM agents can autonomously discover attack algorithms outperforming human-designed methods. This shifts red-teaming from periodic exercises to continuous automated evaluation—a key operational consideration for responsible deployment teams.

2. **Component metrics mislead system safety assessment:** The RAG-for-policy paper shows better retrieval causing worse outcomes through confident hallucination. When discussing evaluation frameworks, emphasize that end-to-end safety metrics matter more than individual component benchmarks.

3. **Quantifiable oversight thresholds for agentic systems:** The Stochastic Gap paper provides formal, auditable metrics (blind-spot mass, oversight-cost identity) that could inform regulatory standards for when AI agents must escalate to human review—directly relevant to EU AI Act high-risk system requirements.

4. **Epistemic verbalization as a safety property:** Self-distillation research reveals that suppressing model uncertainty expression degrades OOD performance by up to 40%. Post-training procedures should preserve, not suppress, uncertainty signals—a consideration for RLHF and distillation pipelines.

5. **Calibration matters for high-stakes deployment:** The medical QA paper demonstrates 49-74% ECE reduction through consistency verification, providing actionable architecture patterns for safety-critical AI systems requiring reliable deferral signals.