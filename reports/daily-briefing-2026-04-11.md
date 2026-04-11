# AI Safety, Governance & Interpretability Briefing
**Date:** 2026-04-11  
**Output:** `reports/daily-briefing-2026-04-11.md`

---

## 🔴 Must-Read (Score 8-10)

### 1. Claudini: Autoresearch Discovers State-of-the-Art Adversarial Attack Algorithms for LLMs
**Link:** [arXiv:2603.24511](https://arxiv.org/abs/2603.24511v1)  
**Score:** 9 | **Tag:** [EVALS]

**So What?** This paper demonstrates that LLM agents can autonomously discover novel white-box adversarial attacks that outperform 30+ existing methods—achieving 100% attack success rate against Meta-SecAlign-70B. This fundamentally changes the red-teaming landscape: defenders must now anticipate AI-accelerated vulnerability discovery, and governance frameworks need to account for automated offensive capabilities.

**Key Takeaway for Interviews:** "The Claudini paper shows that autoresearch pipelines can now automate incremental safety research itself—adversarial attacks optimized by Claude Code transferred directly to break frontier safety measures. This creates urgency for automated defense research and raises questions about responsible disclosure when AI discovers vulnerabilities."

---

### 2. The Stochastic Gap: A Markovian Framework for Pre-Deployment Reliability and Oversight-Cost Auditing in Agentic AI
**Link:** [arXiv:2603.24582](https://arxiv.org/abs/2603.24582v1)  
**Score:** 9 | **Tag:** [SAFETY-OPS]

**So What?** This paper provides a formal framework for quantifying when agentic AI systems can act autonomously versus requiring human oversight, with explicit cost modeling. The "state-action blind mass" concept offers regulators a measurable threshold for deployment safety—exactly what's needed for operationalizing EU AI Act requirements for high-risk autonomous systems.

**Key Takeaway for Interviews:** "The Stochastic Gap framework gives us computable metrics for oversight burden in agentic systems. Their finding that state-action blind mass rises from 1.6% to 12.5% as operational context expands shows why regulatory sandboxes need dynamic monitoring, not static risk assessments."

---

### 3. Retrieval Improvements Do Not Guarantee Better Answers: A Study of RAG for AI Policy QA
**Link:** [arXiv:2603.24580](https://arxiv.org/abs/2603.24580v1)  
**Score:** 8 | **Tag:** [GOVERNANCE]

**So What?** Using the AGORA corpus of 947 AI policy documents, this study reveals a counterintuitive failure mode: stronger retrieval can lead to *more confident hallucinations* when relevant documents are absent. For governance applications where accuracy is critical—policy interpretation, regulatory compliance—this undermines the assumption that RAG provides grounded, reliable answers.

**Key Takeaway for Interviews:** "This paper is essential for anyone building policy analysis tools: domain-specific fine-tuning improved retrieval metrics but didn't improve end-to-end QA performance. It suggests we need faithfulness guarantees beyond retrieval quality when deploying AI for regulatory interpretation."

---

## 🟡 Worth Knowing (Score 5-7)

### 4. Anti-I2V: Safeguarding your photos from malicious image-to-video generation
**Link:** [arXiv:2603.24570](https://arxiv.org/abs/2603.24570v1)  
**Score:** 7 | **Tag:** [SAFETY-OPS]

Introduces adversarial defenses against misuse of image-to-video diffusion models (including DiT architectures), offering practical protective perturbations—relevant for deepfake governance discussions.

---

### 5. A Sociolinguistic Analysis of Automatic Speech Recognition Bias in Newcastle English
**Link:** [arXiv:2603.24549](https://arxiv.org/abs/2603.24549v1)  
**Score:** 6 | **Tag:** [GOVERNANCE]

Demonstrates that ASR errors are socially patterned (gender, age, socioeconomic status), not random—providing empirical grounding for algorithmic fairness requirements in speech technology regulation.

---

### 6. No Single Metric Tells the Whole Story: A Multi-Dimensional Evaluation Framework for Uncertainty Attributions
**Link:** [arXiv:2603.24524](https://arxiv.org/abs/2603.24524v1)  
**Score:** 6 | **Tag:** [ALIGNMENT]

Proposes a systematic framework for evaluating uncertainty attribution methods using the Co-12 XAI framework, finding low inter-method agreement—relevant for interpretability standards in deployment.

---

### 7. Multi-Agent Reasoning with Consistency Verification Improves Uncertainty Calibration in Medical MCQA
**Link:** [arXiv:2603.24481](https://arxiv.org/abs/2603.24481v1)  
**Score:** 6 | **Tag:** [SAFETY-OPS]

Achieves 49-74% reduction in expected calibration error for medical AI through multi-agent verification—demonstrates practical approaches to uncertainty quantification for safety-critical deferral decisions.

---

### 8. Why Does Self-Distillation (Sometimes) Degrade the Reasoning Capability of LLMs?
**Link:** [arXiv:2603.24472](https://arxiv.org/abs/2603.24472v1)  
**Score:** 5 | **Tag:** [ALIGNMENT]

Finds that self-distillation suppresses "epistemic verbalization" (uncertainty expression), causing up to 40% OOD performance drops—relevant for understanding alignment training side effects.

---

## 🟢 Landscape Awareness (Score 1-4)

- **Polynomial Speedup in Diffusion Models with Multilevel Euler-Maruyama** | Academic | Sampling efficiency, no safety implications
- **DreamerAD: Efficient RL via Latent World Model for Autonomous Driving** | Academic | AV simulation, peripheral to AI safety
- **EndoVGGT: GNN-Enhanced Depth Estimation for Surgical 3D Reconstruction** | Academic | Medical imaging, application-specific
- **Chameleon: Episodic Memory for Long-Horizon Robotic Manipulation** | Academic | Robotics memory architecture
- **VFIG: Vectorizing Complex Figures in SVG with VLMs** | Academic | Document processing tooling
- **Completeness of Unbounded Best-First Minimax** | Academic | Game theory algorithms
- **Trust Region Constrained Bayesian Optimization** | Academic | Optimization methods
- **RAVEN: Recurrence-Aware Foundation Models for Clinical Records** | Academic | Healthcare ML
- **The Free-Market Algorithm** | Academic | Novel metaheuristic
- **LensWalk: Agentic Video Understanding** | Academic | Video reasoning agents
- **Evaluating Chunking Strategies for RAG in Oil and Gas** | Industry | Domain-specific RAG
- **UI-Voyager: Self-Evolving GUI Agent** | Academic | GUI automation
- **From Liar Paradox to Incongruent Sets** | Academic | Formal semantics
- **TuneShift-KD: Knowledge Distillation for Fine-tuned Models** | Academic | Model transfer techniques
- **AVO: Agentic Variation Operators for Evolutionary Search** | NVIDIA | Kernel optimization
- **Towards Safe Learning-Based NMPC through RNN Modeling** | Academic | Control systems safety
- **Project and Generate: Divergence-Free Neural Operators** | Academic | Physics-constrained ML
- **Uniform Laws of Large Numbers in Product Spaces** | Academic | Learning theory
- **Composer 2 Technical Report** | Cursor | Coding agents, commercial
- **Conformalized Transfer Learning for Li-ion Battery SOH** | Academic | Battery forecasting

---

## 📌 This Week's Interview Talking Points

1. **Automated Red-Teaming Changes Everything:** The Claudini paper demonstrates that LLM agents can now autonomously discover adversarial attacks that surpass all 30+ existing methods. This isn't incremental—it suggests frontier labs need automated defense research, and policymakers should consider how vulnerability discovery acceleration affects responsible disclosure timelines.

2. **Quantifying Oversight for Agentic Systems:** The Stochastic Gap paper provides the first formal, deployable framework for measuring when AI agents need human oversight versus autonomous operation. The "state-action blind mass" metric could become a regulatory compliance tool—especially relevant as the EU AI Act implementation guidance develops for autonomous agents.

3. **RAG Reliability Warning for Policy Applications:** The AGORA study reveals that better retrieval doesn't guarantee better answers—and can actually produce more confident hallucinations. Anyone building AI tools for regulatory interpretation or policy analysis needs to understand this failure mode before deployment.

4. **Calibration Over Accuracy for Safety-Critical AI:** The medical MCQA paper shows that multi-agent verification with consistency checking can reduce calibration error by 49-74%. This is the kind of "know what you don't know" capability that makes human-AI teaming actually work in high-stakes settings.

5. **Socially-Patterned AI Bias Demands Disaggregated Evaluation:** The ASR bias study provides concrete evidence that system errors correlate with demographic variables. This type of sociolinguistic analysis should inform how we write evaluation requirements in AI governance frameworks—aggregate metrics hide disparate impact.