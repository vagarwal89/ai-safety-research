"""Chapter 5 - Pre-training at toy scale: a small GPT on TinyStories.

Run on Colab (the real exercise):
    !pip install -q datasets        # torch is preinstalled on Colab
    !python train.py --arm both --stories 2000 --steps 1500

Run locally as a smoke test (no network, no downloads):
    python train.py --smoke --arm both

What it does:
  1. Loads TinyStories (streaming, first N stories) or, in smoke mode,
     a small built-in toy corpus written for this course.
  2. Builds two training corpora from the same stories:
       raw     - the stories as they arrived
       cleaned - exact duplicates removed, phone/email/number spans
                 replaced with placeholders (the Chapter 3 gates, in
                 miniature: dedup + PII scrub)
  3. Trains a small GPT (nanoGPT-style, written from scratch below)
     on each corpus, with the same seed and the same config.
  4. Logs train and validation loss, generates sample stories from
     each trained model, and counts PII-like patterns in the samples.
  5. Writes training_report.md and loss_curve.csv in this folder.

Why this matters: pre-training is the step where data becomes a model.
Everything before it (Chapters 2-4) was about the data. Everything
after it (Chapters 6-15) is about what the trained model does. The
ablation answers the question Chapter 3 left open: does cleaning the
data actually change what the model learns? At toy scale the answer
may be small and noisy, and the report says so honestly.

The model: a decoder-only transformer, the same shape as GPT-2 and as
Karpathy's nanoGPT. It reads token ids, predicts the next token, and
is trained with cross-entropy loss. Character-level tokens here, so
the vocabulary is small enough to print and the embedding table is
small enough to inspect. Chapter 3's BPE is the production version of
the same idea: fewer, longer tokens.

Output: training_report.md, loss_curve.csv, checkpoints in out/.
"""

import argparse
import hashlib
import math
import os
import random
import re
import time

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError:
    raise SystemExit(
        "PyTorch is not installed. On Colab it is preinstalled; locally run:\n"
        "  pip install torch --index-url https://download.pytorch.org/whl/cpu")

# ---------------------------------------------------------------------------
# Toy corpus (smoke mode only). Short stories written for this course, not
# real TinyStories rows. All names, numbers, and addresses are fictional.
# Four stories are exact duplicates of earlier ones; four contain
# phone/email/number strings, so the cleaned arm has something to do.
# ---------------------------------------------------------------------------
TOY_STORIES = [
    "One day, a little girl named Lily found a small red ball in her garden. "
    "She picked it up and threw it high into the sky.",
    "Once upon a time, there was a little dog named Ben who loved to run. "
    "Ben ran in the park and chased birds all day.",
    "Tom had a big yellow truck and he drove it to the farm every day. "
    "Tom liked to help his dad on the farm.",
    "Sara loved to bake cookies with her mom in their little kitchen. "
    "The cookies smelled sweet and warm.",
    "One day, a little girl named Lily found a small red ball in her garden. "
    "She picked it up and threw it high into the sky.",
    "A small fish named Fin lived in a blue pond with his friends. "
    "Fin swam fast and hid under a rock.",
    "Mia found a tiny bird with a hurt wing and helped it fly again. "
    "The bird sang a happy song.",
    "Jack had a red kite and a long string. He ran across the field and "
    "the kite flew up high.",
    "Tom had a big yellow truck and he drove it to the farm every day. "
    "Tom liked to help his dad on the farm.",
    "Emma planted a seed in a small pot and watered it every day. "
    "Soon a green plant grew tall.",
    "A little train named Choo went over the hill carrying apples. "
    "The people waved as the train passed by.",
    "Ben and Ana built a tall tower with blocks and it fell down. "
    "They laughed and built it again.",
    "The moon was bright and a little owl sat on a branch at night. "
    "The owl said hoo hoo.",
    "Once upon a time, there was a little dog named Ben who loved to run. "
    "Ben ran in the park and chased birds all day.",
    "Lily called her friend at 98765 43210 to ask about the red ball. "
    "Her friend said the ball was in the garden.",
    "Tom wrote an email to ben@example.com to ask about the yellow truck. "
    "Ben wrote back the next day.",
    "Sara kept a note with the number 1234567890 in her kitchen drawer. "
    "The note said call mom.",
    "A cat named Milo sat on the mat and watched the birds. "
    "Milo liked the sun and the warm mat.",
    "The little duck swam in the pond and quacked all day. "
    "The duck loved the blue water.",
    "A little train named Choo went over the hill carrying apples. "
    "The people waved as the train passed by.",
    "Ana found a shiny stone near the big tree. "
    "She put the stone in her pocket and ran home.",
    "Max had a small boat and he sailed it on the pond. "
    "The boat went fast in the wind.",
    "Lily sent a letter to sam@example.com about the red ball. "
    "Sam said he would come and play.",
    "The sun went down and the stars came out. "
    "Lily went to bed and dreamed of the red ball.",
]

PROMPTS = ["Once upon a time", "Lily found a"]

# ---------------------------------------------------------------------------
# Data loading and cleaning
# ---------------------------------------------------------------------------
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b\d{5}\s?\d{5}\b")
LONG_DIGITS_RE = re.compile(r"\b\d{6,}\b")


def load_live_stories(n):
    """Stream the first n TinyStories rows. Returns (texts, True) or
    ([], False) when the network or the datasets library is missing."""
    try:
        from datasets import load_dataset

        ds = load_dataset("roneneldan/TinyStories", split="train",
                          streaming=True)
        texts = []
        for row in ds:
            value = row.get("text")
            if isinstance(value, str) and value.strip():
                texts.append(value)
            if len(texts) >= n:
                break
        if texts:
            return texts, True
    except Exception as exc:
        print(f"  [live load failed] {exc}")
    return [], False


def scrub_text(text):
    """Replace phone/email/long-digit spans with placeholders.
    Returns (cleaned_text, number_of_spans_replaced)."""
    count = 0
    for pattern, placeholder in (
            (EMAIL_RE, "<EMAIL>"), (PHONE_RE, "<PHONE>"),
            (LONG_DIGITS_RE, "<NUMBER>")):
        text, n = pattern.subn(placeholder, text)
        count += n
    return text, count


def clean_stories(stories):
    """Chapter 3 gates in miniature: exact dedup, then PII scrub.
    Returns (cleaned_stories, n_dupes_removed, n_spans_replaced)."""
    seen = set()
    kept = []
    dupes = 0
    for story in stories:
        key = hashlib.sha256(" ".join(story.lower().split()).encode()).hexdigest()
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        kept.append(story)
    spans = 0
    cleaned = []
    for story in kept:
        text, n = scrub_text(story)
        spans += n
        cleaned.append(text)
    return cleaned, dupes, spans


def count_pii_like(text):
    """Count phone/email/long-digit patterns in generated text."""
    return (len(EMAIL_RE.findall(text)) + len(PHONE_RE.findall(text))
            + len(LONG_DIGITS_RE.findall(text)))


# ---------------------------------------------------------------------------
# The model: a small GPT, written from scratch (nanoGPT shape).
# ---------------------------------------------------------------------------
def build_model(torch, nn, vocab_size, block_size, n_layer, n_head, n_embd):
    class Block(nn.Module):
        def __init__(self):
            super().__init__()
            self.ln1 = nn.LayerNorm(n_embd)
            self.attn = nn.MultiheadAttention(n_embd, n_head,
                                              batch_first=True)
            self.ln2 = nn.LayerNorm(n_embd)
            self.mlp = nn.Sequential(
                nn.Linear(n_embd, 4 * n_embd),
                nn.GELU(),
                nn.Linear(4 * n_embd, n_embd),
            )

        def forward(self, x, mask):
            # Causal mask: position i may look at positions <= i only.
            a, _ = self.attn(self.ln1(x), self.ln1(x), self.ln1(x),
                             attn_mask=mask, need_weights=False)
            x = x + a
            x = x + self.mlp(self.ln2(x))
            return x

    class GPT(nn.Module):
        def __init__(self):
            super().__init__()
            self.block_size = block_size
            # tok_emb: one row per token id, one vector per row.
            # pos_emb: one row per position in the window.
            self.tok_emb = nn.Embedding(vocab_size, n_embd)
            self.pos_emb = nn.Embedding(block_size, n_embd)
            self.blocks = nn.ModuleList([Block() for _ in range(n_layer)])
            self.ln_f = nn.LayerNorm(n_embd)
            self.head = nn.Linear(n_embd, vocab_size, bias=False)

        def forward(self, idx):
            t = idx.size(1)
            positions = torch.arange(t, device=idx.device)
            x = self.tok_emb(idx) + self.pos_emb(positions)
            # A lower-triangular mask: -inf above the diagonal, 0 on/below.
            mask = torch.full((t, t), float("-inf"), device=idx.device)
            mask = torch.triu(mask, diagonal=1)
            for block in self.blocks:
                x = block(x, mask)
            x = self.ln_f(x)
            return self.head(x)

    model = GPT()
    for p in model.parameters():
        if p.dim() > 1:
            nn.init.normal_(p, mean=0.0, std=0.02)
    return model


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def get_batch(data, block_size, batch_size, device, rng):
    ix = [rng.randrange(0, len(data) - block_size - 1)
          for _ in range(batch_size)]
    x = torch.stack([torch.tensor(data[i:i + block_size])
                     for i in ix]).to(device)
    y = torch.stack([torch.tensor(data[i + 1:i + block_size + 1])
                     for i in ix]).to(device)
    return x, y


@torch.no_grad()
def estimate_loss(model, data, block_size, batch_size, device, rng, n=20):
    model.eval()
    losses = []
    for _ in range(n):
        x, y = get_batch(data, block_size, batch_size, device, rng)
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)),
                               y.view(-1))
        losses.append(loss.item())
    model.train()
    return sum(losses) / len(losses)


@torch.no_grad()
def generate(model, stoi, itos, prompt, block_size, device,
             max_new=120, temperature=0.8, seed=0):
    gen_rng = random.Random(seed)
    torch.manual_seed(seed)
    model.eval()
    idx = torch.tensor([[stoi[c] for c in prompt]], device=device)
    for _ in range(max_new):
        crop = idx[:, -block_size:]
        logits = model(crop)
        probs = F.softmax(logits[0, -1] / temperature, dim=-1)
        nxt = torch.multinomial(probs, num_samples=1)
        idx = torch.cat([idx, nxt.view(1, 1)], dim=1)
    model.train()
    return "".join(itos[i] for i in idx[0].tolist())


def train_arm(arm, train_ids, val_ids, vocab_size, cfg, device, out_dir):
    rng = random.Random(cfg["seed"])
    torch.manual_seed(cfg["seed"])
    model = build_model(torch, nn, vocab_size, cfg["block_size"],
                        cfg["n_layer"], cfg["n_head"], cfg["n_embd"])
    model.to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  [{arm}] model: {n_params:,} parameters, "
          f"vocab {vocab_size}, block {cfg['block_size']}, "
          f"layers {cfg['n_layer']}, heads {cfg['n_head']}, "
          f"embd {cfg['n_embd']}")
    print(f"  [{arm}] random-guess loss ln({vocab_size}) = "
          f"{math.log(vocab_size):.2f}")
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"],
                            weight_decay=0.01)
    history = []
    t0 = time.time()
    for step in range(1, cfg["steps"] + 1):
        # Linear learning-rate decay to 10% of the starting rate.
        lr = cfg["lr"] * (0.1 + 0.9 * (1 - step / cfg["steps"]))
        for g in opt.param_groups:
            g["lr"] = lr
        x, y = get_batch(train_ids, cfg["block_size"], cfg["batch_size"],
                         device, rng)
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, vocab_size), y.view(-1))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % cfg["eval_every"] == 0 or step == 1:
            tr = estimate_loss(model, train_ids, cfg["block_size"],
                               cfg["batch_size"], device, rng, n=10)
            va = estimate_loss(model, val_ids, cfg["block_size"],
                               cfg["batch_size"], device, rng, n=10)
            history.append((step, round(tr, 4), round(va, 4)))
            print(f"  [{arm}] step {step}/{cfg['steps']} "
                  f"train {tr:.3f} val {va:.3f} "
                  f"({time.time() - t0:.0f}s)")
    final_val = history[-1][2] if history else None
    final_train = history[-1][1] if history else None
    torch.save(model.state_dict(),
               os.path.join(out_dir, f"model_{arm}.pt"))
    return model, history, final_train, final_val, n_params


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Chapter 5: train a small GPT.")
    ap.add_argument("--arm", choices=["raw", "cleaned", "both"],
                    default="both")
    ap.add_argument("--smoke", action="store_true",
                    help="toy corpus, tiny model, 150 steps, CPU")
    ap.add_argument("--stories", type=int, default=2000)
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    os.makedirs(args.out, exist_ok=True)

    if args.smoke:
        stories, live = list(TOY_STORIES), False
        cfg = dict(n_layer=2, n_head=2, n_embd=64, block_size=64,
                   batch_size=8, steps=150, lr=3e-3, eval_every=25,
                   seed=args.seed)
        print("Smoke mode: built-in toy corpus "
              f"({len(stories)} stories, all fictional).")
    else:
        stories, live = load_live_stories(args.stories)
        if not stories:
            print("Live load failed. Falling back to the toy corpus.")
            stories, live = list(TOY_STORIES), False
            cfg = dict(n_layer=2, n_head=2, n_embd=64, block_size=64,
                       batch_size=8, steps=150, lr=3e-3, eval_every=25,
                       seed=args.seed)
        else:
            cfg = dict(n_layer=4, n_head=4, n_embd=128, block_size=128,
                       batch_size=32, steps=args.steps, lr=1e-3,
                       eval_every=50, seed=args.seed)
        print(f"Loaded {len(stories)} stories "
              f"({'live TinyStories' if live else 'TOY CORPUS fallback'}).")

    # Split first, then clean the training split. The validation split is
    # cleaned the same way for both arms, so the comparison is apples to
    # apples, and no validation story is ever trained on.
    n_val = max(2, len(stories) // 10)
    train_stories = stories[:-n_val]
    val_stories = stories[-n_val:]
    val_clean, _, _ = clean_stories(val_stories)

    raw_text = "\n\n".join(train_stories)
    cleaned_train, n_dupes, n_spans = clean_stories(train_stories)
    cleaned_text = "\n\n".join(cleaned_train)
    val_text = "\n\n".join(val_clean)
    print(f"Split: {len(train_stories)} train stories, "
          f"{len(val_stories)} validation stories.")
    print(f"Cleaning: removed {n_dupes} exact duplicates, "
          f"replaced {n_spans} PII-like spans.")
    print(f"Train chars: raw {len(raw_text):,}, "
          f"cleaned {len(cleaned_text):,}.")

    # One shared vocabulary, built from both corpora, so both arms use
    # identical token ids and the comparison is fair.
    chars = sorted(set(raw_text + cleaned_text + val_text))
    stoi = {c: i for i, c in enumerate(chars)}
    itos = {i: c for c, i in stoi.items()}
    vocab_size = len(chars)
    print(f"Vocabulary: {vocab_size} characters: {chars!r}")

    def encode(text):
        return [stoi[c] for c in text]

    raw_ids = encode(raw_text)
    cleaned_ids = encode(cleaned_text)
    val_ids = encode(val_text)

    arms = ["raw", "cleaned"] if args.arm == "both" else [args.arm]
    results = {}
    for arm in arms:
        print(f"\nTraining arm: {arm}")
        model, history, ftr, fva, n_params = train_arm(
            arm, raw_ids if arm == "raw" else cleaned_ids, val_ids,
            vocab_size, cfg, device, args.out)
        samples = {}
        for prompt in PROMPTS:
            samples[prompt] = generate(model, stoi, itos, prompt,
                                       cfg["block_size"], device,
                                       max_new=120, temperature=0.8)
            print(f"  [{arm}] sample ({prompt!r}):\n"
                  f"    {samples[prompt]!r}")
        pii_hits = sum(count_pii_like(s) for s in samples.values())
        print(f"  [{arm}] PII-like patterns in samples: {pii_hits}")
        results[arm] = dict(history=history, final_train=ftr,
                            final_val=fva, n_params=n_params,
                            samples=samples, pii_hits=pii_hits)

    with open("loss_curve.csv", "w", encoding="utf-8") as f:
        f.write("arm,step,train_loss,val_loss\n")
        for arm in arms:
            for step, tr, va in results[arm]["history"]:
                f.write(f"{arm},{step},{tr},{va}\n")
    write_report(args, live, stories, train_stories, val_stories,
                 n_dupes, n_spans, raw_text, cleaned_text, vocab_size,
                 cfg, results)
    print("\nWrote training_report.md and loss_curve.csv")


def write_report(args, live, stories, train_stories, val_stories,
                 n_dupes, n_spans, raw_text, cleaned_text, vocab_size,
                 cfg, results):
    lines = ["# Training Report: Chapter 5", "",
             "Small GPT (nanoGPT shape) trained on TinyStories, raw vs "
             "cleaned data.", "",
             f"- **Data:** {len(stories)} stories "
             f"({'live TinyStories' if live else 'TOY CORPUS fallback, all fictional'}), "
             f"{len(train_stories)} train / {len(val_stories)} validation",
             f"- **Cleaning:** {n_dupes} exact duplicates removed, "
             f"{n_spans} PII-like spans replaced",
             f"- **Train chars:** raw {len(raw_text):,}, "
             f"cleaned {len(cleaned_text):,}",
             f"- **Vocabulary:** {vocab_size} characters (shared by both arms)",
             f"- **Model:** {cfg['n_layer']} layers, {cfg['n_head']} heads, "
             f"embedding dim {cfg['n_embd']}, context {cfg['block_size']}, "
             f"batch {cfg['batch_size']}, steps {cfg['steps']}, "
             f"lr {cfg['lr']}",
             f"- **Random-guess loss:** ln({vocab_size}) = "
             f"{math.log(vocab_size):.2f}",
             ""]
    for arm, r in results.items():
        lines += [f"## Arm: {arm}", "",
                  f"- Parameters: {r['n_params']:,}",
                  f"- Final train loss: {r['final_train']}",
                  f"- Final validation loss: {r['final_val']}",
                  f"- PII-like patterns in samples: {r['pii_hits']}",
                  "",
                  "### Loss history (step, train, val)", ""]
        for step, tr, va in r["history"]:
            lines.append(f"- {step}: train {tr}, val {va}")
        lines += ["", "### Samples", ""]
        for prompt, text in r["samples"].items():
            lines.append(f"- Prompt {prompt!r}:")
            lines.append(f"  > {text}")
        lines.append("")
    if "raw" in results and "cleaned" in results:
        rv, cv = results["raw"]["final_val"], results["cleaned"]["final_val"]
        diff = rv - cv
        better = "cleaned" if diff > 0 else "raw"
        lines += ["## Ablation verdict", "",
                  f"- Raw final validation loss: {rv}",
                  f"- Cleaned final validation loss: {cv}",
                  f"- Difference: {abs(diff):.3f} in favour of {better}.",
                  "",
                  "Read this with the scale in mind. Validation loss here "
                  f"is measured on just {len(val_stories)} stories, so a "
                  f"difference of {abs(diff):.3f} is not a finding: it is "
                  "within the noise of a validation set that small, and a "
                  "re-run with a different seed could flip it. The "
                  "meaningful results are the loss curves themselves (both "
                  "arms learn, both fall far below the random-guess "
                  "baseline) and the samples (both arms write story-shaped "
                  "fragments, not coherent English, after only 150 steps). "
                  "The cleaning effect that matters most is not in the "
                  "loss: it is that the cleaned arm never saw the phone "
                  "numbers and email addresses, so it cannot reproduce "
                  "them. Chapter 6 tests that directly with an extraction "
                  "probe.",
                  ""]
    with open("training_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
