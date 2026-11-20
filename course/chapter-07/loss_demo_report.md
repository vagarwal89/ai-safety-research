# Loss demo report (November 20, 2026 run)

One example: prompt "What is a DPIA?", response "A DPIA is a data protection impact assessment."

- Average loss, prompt tokens only: 0.179
- Average loss, response tokens only (SFT loss): 0.523
- Average loss, all tokens (pre-training loss): 0.400
- Prompt tokens: 5 of 14; prompt loss sum 0.896 of total 5.598
- One confident mistake (p=0.05 on 'data'): SFT loss 0.523 -> 0.754; loss on that token alone 2.996

Reading: the unmasked average looks lower than the SFT loss because the easy prompt tokens dilute it. Training on the unmasked loss spends gradient on learning to predict questions. Masking keeps the loss honest: it measures only how well the model produces the answer.
