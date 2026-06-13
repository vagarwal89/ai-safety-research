# AI Safety & Governance Daily Briefing
**Date:** 2026-06-13  
**Coverage Period:** Past 7 days  
**File:** `reports/daily-briefing-2026-06-13.md`

---

## 🔴 Must-Read (Score 8-10)

### 1. Claudini: Autoresearch Discovers State-of-the-Art Adversarial Attack Algorithms for LLMs
**Link:** https://arxiv.org/abs/2603.24511v1  
**Score:** 9 | **Tag:** [EVALS]

**So What?** This paper demonstrates that LLM agents can autonomously discover novel adversarial attacks achieving 100% success rates against safety-tuned models like Meta-SecAlign-70B — a critical finding for regulators assessing whether current safety measures can keep pace with automated red-teaming. The ability to automate vulnerability discovery at this level fundamentally changes the threat model for AI governance frameworks.

**Key Takeaway for Interviews:** "Claudini shows that adversarial red-teaming can now be automated at frontier capability levels. This has direct implications for the EU AI Act's requirement for systematic risk assessment — labs may need to demonstrate robustness against automated attack discovery, not just known attack vectors."

---

### 2. The Stochastic Gap: A Markovian Framework for Pre-Deployment Reliability and Oversight-Cost Auditing in Agentic AI
**Link:** https://arxiv.org/abs/2603.24582v1  
**Score:** 8 | **Tag:** [SAFETY-OPS]

**So What?** This paper provides a rigorous mathematical framework for quantifying when agentic AI systems require human oversight, directly addressing a core challenge in deployment safety. The finding that systems can appear well-supported at the state level while having substantial "blind mass" at the decision level has immediate implications for how regulators should evaluate agentic system deployment readiness.

**Key Takeaway for Interviews:** "The 'stochastic gap' concept formalizes a key intuition in deployment safety: apparent reliability metrics can mask decision-level uncertainty. This framework could inform NIST AI RMF guidance on agentic system oversight requirements."

---

### 3. Retrieval Improvements Do Not Guarantee Better Answers: A Study of RAG for AI Policy QA
**Link:** https://arxiv.org/abs/2603.24580v1  
**Score:** 8 | **Tag:** [GOVERNANCE]

**So What?** Using the AGORA corpus of 947 AI policy documents, this research reveals a counterintuitive and governance-critical finding: better retrieval can actually increase hallucination confidence when relevant documents are absent. For policy institutions deploying RAG systems to analyze regulatory frameworks, this highlights serious reliability concerns that current evaluation methods may miss.

**Key Takeaway for Interviews:** "This paper directly challenges assumptions about AI-assisted policy analysis tools. The finding that improved retrieval can lead to 'more confident hallucinations' is a red flag for institutions using AI to interpret evolving regulatory frameworks like the EU AI Act."

---

## 🟡 Worth Knowing (Score 5-7)

### 4. No Single Metric Tells the Whole Story: A Multi-Dimensional Evaluation Framework for Uncertainty Attributions
**Link:** https://arxiv.org/abs/2603.24524v1  
**Score:** 7 | **Tag:** [ALIGNMENT]

Proposes concrete implementations for evaluating XAI uncertainty attributions using the Co-12 framework; introduces "conveyance" property to test whether epistemic uncertainty propagates to feature-level explanations — relevant for interpretability standards in high-stakes deployment.

---

### 5. Multi-Agent Reasoning with Consistency Verification Improves Uncertainty Calibration in Medical MCQA
**Link:** https://arxiv.org/abs/2603.24481v1  
**Score:** 6 | **Tag:** [SAFETY-OPS]

Demonstrates 49-74% reduction in expected calibration error through two-phase self-verification in medical AI; directly relevant to deferral mechanisms and safety-critical deployment where knowing when to escalate to humans is essential.

---

### 6. Why Does Self-Distillation (Sometimes) Degrade the Reasoning Capability of LLMs?
**Link:** https://arxiv.org/abs/2603.24472v1  
**Score:** 6 | **Tag:** [ALIGNMENT]

Identifies that self-distillation suppresses "epistemic verbalization" (uncertainty expression), causing up to 40% performance drops on OOD problems; important for understanding how training choices affect model robustness and reliability.

---

### 7. Anti-I2V: Safeguarding your photos from malicious image-to-video generation
**Link:** https://arxiv.org/abs/2603.24570v1  
**Score:** 5 | **Tag:** [SAFETY-OPS]

Presents adversarial defense against malicious deepfake video generation from photos; accepted to CVPR 2026; relevant to discussions of synthetic media governance and individual protection measures.

---

### 8. Towards Safe Learning-Based Non-Linear Model Predictive Control through Recurrent Neural Network Modeling
**Link:** https://arxiv.org/abs/2603.24503v1  
**Score:** 5 | **Tag:** [SAFETY-OPS]

Introduces safety-augmented neural policy with online evaluation and fallback mechanisms for robotics control; demonstrates safety-by-design approach relevant to autonomous systems governance.

---

## 🟢 Landscape Awareness (Score 1-4)

- **DreamerAD** — Autonomous driving RL world model, efficiency focus
- **Chameleon: Episodic Memory for Long-Horizon Robotic Manipulation** — Robotics memory architecture
- **Composer 2 Technical Report** — Cursor Research, agentic software engineering model
- **UI-Voyager** — Self-evolving GUI agent via failed experience learning
- **TuneShift-KD** — Knowledge transfer between fine-tuned models without original data
- **AVO: Agentic Variation Operators** — NVIDIA, evolutionary search for kernel optimization
- **LensWalk** — Agentic video understanding framework
- **VFIG: Vectorizing Complex Figures** — Vision-language model for SVG conversion
- **Polynomial Speedup in Diffusion Models** — Multilevel sampling efficiency
- **Evaluating Chunking Strategies for RAG** — Oil & gas enterprise document analysis
- **Completeness of Unbounded Best-First Minimax** — Game-playing algorithm theory
- **RAVEN: Scaling Recurrence-aware Foundation Models** — Clinical EHR modeling
- **Uniform Laws of Large Numbers in Product Spaces** — Learning theory foundations
- **Conformalized Transfer Learning for Li-ion Battery SOH** — Uncertainty quantification for battery forecasting
- **A Sociolinguistic Analysis of ASR Bias** — Newcastle English dialect recognition disparities

---

## 📌 This Week's Interview Talking Points

1. **Automated red-teaming is now frontier-capable:** Claudini's 100% ASR against safety-tuned models demonstrates that adversarial discovery can be automated. This reshapes how labs should think about continuous safety evaluation and has direct implications for regulatory requirements around systematic risk assessment.

2. **Component-level improvements ≠ system-level reliability:** The RAG-for-policy paper shows that better retrieval can paradoxically increase hallucination confidence. This is a cautionary finding for any governance institution deploying AI for regulatory analysis — end-to-end evaluation is essential.

3. **Quantifying oversight requirements for agentic systems:** The "Stochastic Gap" framework provides formal methods to calculate when human-in-the-loop intervention is necessary. This could inform practical implementation of the EU AI Act's human oversight requirements for high-risk AI systems.

4. **Uncertainty expression matters for robustness:** Self-distillation research shows that suppressing uncertainty verbalization in training degrades OOD performance by up to 40%. For safety-critical applications, training procedures that preserve epistemic humility may be essential.

5. **Calibration, not just accuracy, determines deployment readiness:** Multiple papers this week emphasize that well-calibrated uncertainty (knowing when the model doesn't know) is more important for safe deployment than raw accuracy metrics — a key framing for discussing AI safety standards with policy audiences.