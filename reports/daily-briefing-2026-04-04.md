# AI Safety & Governance Daily Briefing
**Date:** 2026-04-04  
**Report Path:** `reports/daily-briefing-2026-04-04.md`

---

## 🔴 Must-Read (Score 8-10)

### 1. Claudini: Autoresearch Discovers State-of-the-Art Adversarial Attack Algorithms for LLMs
**Link:** [arXiv:2603.24511](https://arxiv.org/abs/2603.24511v1)  
**Score:** 9 | **Tag:** [EVALS]

**So What?** This paper demonstrates that LLM agents can autonomously discover novel white-box adversarial attacks that outperform all 30+ existing methods, achieving 100% attack success rate against Meta-SecAlign-70B. This fundamentally changes the threat model for AI safety: adversaries can now automate the discovery of jailbreaks faster than defenders can patch them.

**Key Takeaway for Interviews:** "The Claudini paper shows autoresearch can discover adversarial attacks that break SOTA safety measures—this implies red-teaming must become continuous and automated, not periodic and manual. Policy frameworks need to account for attack discovery becoming commoditized."

---

### 2. The Stochastic Gap: A Markovian Framework for Pre-Deployment Reliability and Oversight-Cost Auditing in Agentic AI
**Link:** [arXiv:2603.24582](https://arxiv.org/abs/2603.24582v1)  
**Score:** 9 | **Tag:** [SAFETY-OPS]

**So What?** This provides the first rigorous mathematical framework for quantifying when agentic AI systems should escalate to human oversight, with tested metrics on 250K+ real enterprise workflow cases. Regulators and deployers now have concrete, auditable thresholds for "blind-spot mass" that determine acceptable autonomous operation boundaries.

**Key Takeaway for Interviews:** "The Stochastic Gap framework gives us auditable pre-deployment metrics for agentic AI reliability—this is exactly what governance frameworks like the EU AI Act need for high-risk system certification. It operationalizes 'appropriate human oversight' with measurable quantities."

---

### 3. Retrieval Improvements Do Not Guarantee Better Answers: A Study of RAG for AI Policy QA
**Link:** [arXiv:2603.24580](https://arxiv.org/abs/2603.24580v1)  
**Score:** 8 | **Tag:** [GOVERNANCE]

**So What?** Using the AGORA corpus of 947 AI policy documents, this study reveals a critical failure mode: stronger retrieval can paradoxically increase confident hallucinations when relevant documents are absent. For policy analysts relying on RAG systems to navigate regulatory frameworks, this undermines trust in AI-assisted governance work.

**Key Takeaway for Interviews:** "This paper directly informs AI governance tooling—it shows component-level improvements don't guarantee system-level reliability for policy QA. Any AI system deployed for regulatory analysis needs holistic end-to-end evaluation, not just retrieval benchmarks."

---

## 🟡 Worth Knowing (Score 5-7)

### 4. No Single Metric Tells the Whole Story: A Multi-Dimensional Evaluation Framework for Uncertainty Attributions
**Link:** [arXiv:2603.24524](https://arxiv.org/abs/2603.24524v1)  
**Score:** 7 | **Tag:** [ALIGNMENT]

Proposes concrete implementations of Co-12 XAI evaluation properties for uncertainty attributions, finding gradient-based methods outperform perturbation-based approaches—relevant for interpretability-based safety cases.

---

### 5. Anti-I2V: Safeguarding Photos from Malicious Image-to-Video Generation
**Link:** [arXiv:2603.24570](https://arxiv.org/abs/2603.24570v1)  
**Score:** 6 | **Tag:** [SAFETY-OPS]

Presents adversarial defenses against deepfake video generation including DiT architectures; addresses misuse prevention for generative AI deployment—accepted to CVPR 2026.

---

### 6. Multi-Agent Reasoning with Consistency Verification Improves Uncertainty Calibration in Medical MCQA
**Link:** [arXiv:2603.24481](https://arxiv.org/abs/2603.24481v1)  
**Score:** 6 | **Tag:** [ALIGNMENT]

Two-phase self-verification reduces expected calibration error by 49-74% in medical QA; demonstrates practical uncertainty quantification for safety-critical deployment deferral decisions.

---

### 7. Why Does Self-Distillation (Sometimes) Degrade the Reasoning Capability of LLMs?
**Link:** [arXiv:2603.24472](https://arxiv.org/abs/2603.24472v1)  
**Score:** 5 | **Tag:** [ALIGNMENT]

Identifies that self-distillation suppresses epistemic verbalization (uncertainty expression), causing up to 40% OOD performance drops—implications for training methods in safety-critical reasoning systems.

---

### 8. Towards Safe Learning-Based Non-Linear Model Predictive Control through Recurrent Neural Network Modeling
**Link:** [arXiv:2603.24503](https://arxiv.org/abs/2603.24503v1)  
**Score:** 5 | **Tag:** [SAFETY-OPS]

Introduces Safe Sequential-AMPC with fallback mechanisms for learned control policies; demonstrates safety-augmented deployment patterns for robotics/autonomous systems.

---

## 🟢 Landscape Awareness (Score 1-4)

- **DreamerAD** — latent world model for autonomous driving RL, 80x speedup claim
- **Chameleon: Episodic Memory for Long-Horizon Robotic Manipulation** — memory architectures for robotics
- **LensWalk: Agentic Video Understanding** — CVPR 2026, agentic perception planning
- **UI-Voyager: Self-Evolving GUI Agent** — 81% success rate on AndroidWorld via RL
- **VFIG: Vectorizing Complex Figures in SVG** — VLM benchmark, compares to GPT-5.2
- **AVO: Agentic Variation Operators** — discovers GPU kernels outperforming cuDNN/FlashAttention-4
- **Composer 2 Technical Report** — Cursor's agentic coding model, frontier-level SWE-bench results
- **Evaluating Chunking Strategies for RAG in Oil and Gas** — enterprise RAG limitations on visual documents
- **EndoVGGT** — surgical 3D reconstruction, medical AI application
- **CliPPER** — surgical video-language pretraining, zero-shot phase recognition

---

## 📌 This Week's Interview Talking Points

1. **Automated Red-Teaming is Now Real:** The Claudini paper demonstrates that LLM agents can discover novel adversarial attacks that break SOTA defenses. This shifts the security paradigm—organizations need continuous automated red-teaming infrastructure, and governance frameworks must anticipate attack discovery becoming commoditized. Reference: "autoresearch discovers attacks achieving 100% ASR against Meta-SecAlign."

2. **Quantifying Human Oversight Requirements:** The Stochastic Gap framework provides auditable, pre-deployment metrics for determining when agentic AI should escalate to humans. This operationalizes EU AI Act "appropriate human oversight" requirements with measurable blind-spot mass thresholds tested on real enterprise workflows.

3. **Component Improvements ≠ System Safety:** The AGORA RAG study shows that better retrieval can paradoxically increase confident hallucinations in policy QA systems. For AI governance tool deployment, end-to-end evaluation is essential—this is a concrete example of why NIST AI RMF emphasizes system-level testing over component benchmarks.

4. **Uncertainty Calibration for Deployment Safety:** Multiple papers this week (medical MCQA calibration, self-distillation degradation) highlight that models must express appropriate uncertainty for safe deployment. The finding that self-distillation suppresses epistemic verbalization has direct implications for training procedures in safety-critical applications.

5. **Frontier Model Safety Implications:** Both Claudini (adversarial) and AVO/Composer 2 (capability) papers show frontier coding agents achieving SOTA performance on complex tasks. The dual-use nature of these capabilities—discovering both attacks and defenses—underscores the urgency of structured access and deployment governance for agentic systems.