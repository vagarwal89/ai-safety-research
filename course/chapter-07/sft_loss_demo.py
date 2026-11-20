"""Chapter 7: the one idea behind SFT, worked by hand.

Pre-training loss (Chapter 5) is the average of -log(p) over EVERY token:
the model is scored on predicting each next token, including the tokens
of the question itself. SFT changes WHICH tokens count: the loss is
computed only on the RESPONSE tokens. The prompt tokens are masked out,
so the model is never rewarded for predicting questions, only for
producing answers.

Loss recap, one line: for one token, loss = -ln(probability the model
gave the true next token). A probability of 1 gives loss 0. A
probability of 0.5 gives loss 0.69. A probability of 0.05 gives loss
3.00. Lower probability on the true token means higher loss.

Run: python sft_loss_demo.py
Writes: loss_demo_report.md
"""

import math

# One training example, split into prompt tokens and response tokens.
# Tokens here are words, so the masking is visible. A real tokenizer
# splits words into subword pieces, but the idea is identical.
PROMPT_TOKENS = ["What", "is", "a", "DPIA", "?"]
RESPONSE_TOKENS = ["A", "DPIA", "is", "a", "data", "protection",
                   "impact", "assessment", "."]

# Made-up probabilities the model gives to the TRUE next token at each
# position. The prompt is formulaic, so the model predicts it easily
# (high probabilities). The response is harder (lower probabilities).
PROMPT_PROBS = [0.9, 0.8, 0.9, 0.7, 0.9]
RESPONSE_PROBS = [0.6, 0.5, 0.7, 0.8, 0.4, 0.5, 0.6, 0.5, 0.9]


def token_loss(p):
    """Loss for one token: -ln(probability of the true token)."""
    return -math.log(p)


def average(losses):
    return sum(losses) / len(losses)


def main():
    prompt_losses = [token_loss(p) for p in PROMPT_PROBS]
    response_losses = [token_loss(p) for p in RESPONSE_PROBS]

    print("Per-token loss, prompt tokens (masked out in SFT):")
    for tok, p, loss in zip(PROMPT_TOKENS, PROMPT_PROBS, prompt_losses):
        print(f"  {tok!r:>14}  p={p:.2f}  loss={loss:.3f}")
    print("Per-token loss, response tokens (trained on in SFT):")
    for tok, p, loss in zip(RESPONSE_TOKENS, RESPONSE_PROBS, response_losses):
        print(f"  {tok!r:>14}  p={p:.2f}  loss={loss:.3f}")

    masked = average(response_losses)
    unmasked = average(prompt_losses + response_losses)
    prompt_avg = average(prompt_losses)
    print(f"\nAverage loss, prompt tokens only:   {prompt_avg:.3f}")
    print(f"Average loss, response tokens only (SFT loss): {masked:.3f}")
    print(f"Average loss, ALL tokens (pre-training loss):  {unmasked:.3f}")
    print(f"Prompt tokens are {len(PROMPT_TOKENS)} of "
          f"{len(PROMPT_TOKENS) + len(RESPONSE_TOKENS)} tokens, "
          f"but carry only {sum(prompt_losses):.3f} of "
          f"{sum(prompt_losses) + sum(response_losses):.3f} total loss.")

    # Second demo: one confident mistake. Change the model's probability
    # on the token "data" from 0.4 to 0.05 and watch the average move.
    bad_probs = list(RESPONSE_PROBS)
    bad_probs[4] = 0.05
    bad_losses = [token_loss(p) for p in bad_probs]
    print("\nSame response, but the model gives 'data' probability 0.05:")
    print(f"  loss on 'data' alone: {token_loss(0.05):.3f}")
    print(f"  SFT loss rises from {masked:.3f} to {average(bad_losses):.3f}")
    print("  One confident wrong token dominates the average. That is "
          "why a single hallucinated fact is expensive in SFT loss, "
          "and why the loss falls fastest when the model stops "
          "guessing on hard tokens.")

    with open("loss_demo_report.md", "w") as f:
        f.write("# Loss demo report (November 20, 2026 run)\n\n")
        f.write("One example: prompt \"What is a DPIA?\", response "
                "\"A DPIA is a data protection impact assessment.\"\n\n")
        f.write(f"- Average loss, prompt tokens only: {prompt_avg:.3f}\n")
        f.write(f"- Average loss, response tokens only (SFT loss): "
                f"{masked:.3f}\n")
        f.write(f"- Average loss, all tokens (pre-training loss): "
                f"{unmasked:.3f}\n")
        f.write(f"- Prompt tokens: {len(PROMPT_TOKENS)} of "
                f"{len(PROMPT_TOKENS) + len(RESPONSE_TOKENS)}; "
                f"prompt loss sum {sum(prompt_losses):.3f} of total "
                f"{sum(prompt_losses) + sum(response_losses):.3f}\n")
        f.write(f"- One confident mistake (p=0.05 on 'data'): SFT loss "
                f"{masked:.3f} -> {average(bad_losses):.3f}; "
                f"loss on that token alone {token_loss(0.05):.3f}\n")
        f.write("\nReading: the unmasked average looks lower than the "
                "SFT loss because the easy prompt tokens dilute it. "
                "Training on the unmasked loss spends gradient on "
                "learning to predict questions. Masking keeps the loss "
                "honest: it measures only how well the model produces "
                "the answer.\n")
    print("\nWrote loss_demo_report.md")


if __name__ == "__main__":
    main()
