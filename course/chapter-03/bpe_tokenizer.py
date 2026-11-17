"""Chapter 3 - Byte Pair Encoding (BPE) tokenizer, from scratch.

Run:  python bpe_tokenizer.py

Needs: pip install datasets   (only for the live TinyStories sample;
      the script falls back to a small embedded sample if the
      download fails, and says so clearly in the report.)

What it does:
  1. Loads a sample of TinyStories (100 stories by default).
  2. Trains a BPE tokenizer on it: start with single characters,
     then repeatedly merge the most frequent adjacent pair, 100 times.
     This is the same idea behind the tokenizers in GPT-2 and Llama,
     in miniature. The original algorithm is Sennrich et al., 2016.
  3. Encodes three test sentences, decodes them back, and checks the
     round trip. It also encodes an unseen word to show the key BPE
     property: any word can be represented, because unknown words
     fall back to single characters.
  4. Reports the compression: tokens per word, and the most frequent
     merges the tokenizer learned.

Why this matters: a model never sees words or letters. It sees token
ids, integers from a fixed vocabulary. The tokenizer decides what
those integers mean, how long a text becomes, and what the model can
and cannot represent cleanly. Cleaning changes the text; tokenizing
decides how the model reads it. Both shape training, and both belong
in the Article 10(2)(c) preparation record.

Output: tokenizer_report.md in this folder.
"""

import re
from collections import Counter

NUM_MERGES = 100
SAMPLE_SIZE = 100
END_MARKER = "</w>"

# Small embedded sample, used only when the network is unavailable.
# Short stories written for this course, not real TinyStories rows.
FALLBACK_STORIES = [
    "One day, a little girl named Lily found a small red ball in her garden.",
    "Once upon a time, there was a little dog named Ben who loved to run.",
    "Tom had a big yellow truck and he drove it to the farm every day.",
    "Sara loved to bake cookies with her mom in their little kitchen.",
    "A small fish named Fin lived in a blue pond with his friends.",
    "Mia found a tiny bird with a hurt wing and helped it fly again.",
    "Jack had a red kite and a long string and he ran across the field.",
    "Emma planted a seed in a small pot and watered it every day.",
    "A little train named Choo went over the hill carrying apples.",
    "Ben and Ana built a tall tower with blocks and it fell down.",
    "The moon was bright and a little owl sat on a branch at night.",
    "Lily laughed and ran to get the ball near the big tree.",
]

TEST_SENTENCES = [
    "The little cat sat on the mat.",
    "Lily found a red ball in the garden.",
    "The xylophone played a quiet song.",
]


def load_stories(n=SAMPLE_SIZE):
    """Stream the first n TinyStories rows, or fall back to the sample."""
    try:
        from datasets import load_dataset

        ds = load_dataset("roneneldan/TinyStories", split="train", streaming=True)
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
        print(f"  [streaming sample failed] {exc}")
    return list(FALLBACK_STORIES), False


def word_counts(texts):
    """Lowercased words and their frequencies across the corpus."""
    counts = Counter()
    for text in texts:
        for word in re.findall(r"[a-z]+", text.lower()):
            counts[word] += 1
    return counts


def train_bpe(counts, num_merges=NUM_MERGES):
    """Train BPE. Returns (merges, vocab).

    merges is the ordered list of merged pairs, e.g. [("t", "h"), ...].
    vocab maps each word to its current token tuple.
    """
    vocab = {}
    for word in counts:
        vocab[word] = tuple(word) + (END_MARKER,)

    merges = []
    for step in range(num_merges):
        pair_counts = Counter()
        for word, freq in counts.items():
            tokens = vocab[word]
            for i in range(len(tokens) - 1):
                pair_counts[(tokens[i], tokens[i + 1])] += freq
        if not pair_counts:
            break
        best_pair, best_count = pair_counts.most_common(1)[0]
        merges.append(best_pair)
        merged_token = "".join(best_pair)
        new_vocab = {}
        for word, tokens in vocab.items():
            new_tokens = []
            i = 0
            while i < len(tokens):
                if (i < len(tokens) - 1
                        and (tokens[i], tokens[i + 1]) == best_pair):
                    new_tokens.append(merged_token)
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            new_vocab[word] = tuple(new_tokens)
        vocab = new_vocab
        if step < 5 or (step + 1) % 25 == 0:
            print(f"  merge {step + 1}: {best_pair} -> "
                  f"'{merged_token}' ({best_count} times)")
    return merges, vocab


def encode_word(word, merges):
    """Encode one word by applying the learned merges in order."""
    tokens = list(word.lower()) + [END_MARKER]
    for pair in merges:
        merged = "".join(pair)
        new_tokens = []
        i = 0
        while i < len(tokens):
            if (i < len(tokens) - 1
                    and (tokens[i], tokens[i + 1]) == pair):
                new_tokens.append(merged)
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens
    return tokens


def encode_sentence(sentence, merges):
    tokens = []
    for word in re.findall(r"[a-z]+", sentence.lower()):
        tokens.extend(encode_word(word, merges))
    return tokens


def decode_tokens(tokens):
    """Join tokens back into text. The end marker becomes a space."""
    text = "".join(tokens)
    return text.replace(END_MARKER, " ").strip()


def main():
    texts, live = load_stories()
    print(f"Loaded {len(texts)} stories "
          f"({'live TinyStories data' if live else 'FALLBACK SAMPLE, network unavailable'})")
    counts = word_counts(texts)
    print(f"Corpus: {sum(counts.values())} words, {len(counts)} unique words")
    print(f"Training BPE with {NUM_MERGES} merges ...")

    merges, vocab = train_bpe(counts)
    vocab_size = len(set(t for tokens in vocab.values() for t in tokens))
    print(f"\nLearned {len(merges)} merges. Vocabulary size: {vocab_size} tokens.")

    print("\nFirst 15 merges (most frequent pairs first):")
    for i, pair in enumerate(merges[:15]):
        print(f"  {i + 1}. {pair} -> '{''.join(pair)}'")

    print("\nEncoding test sentences:")
    results = []
    for sentence in TEST_SENTENCES:
        tokens = encode_sentence(sentence, merges)
        decoded = decode_tokens(tokens)
        words = re.findall(r"[a-z]+", sentence.lower())
        ratio = len(tokens) / len(words) if words else 0
        round_trip = decoded == sentence.lower().rstrip(".")
        results.append((sentence, tokens, decoded, ratio, round_trip))
        print(f"  '{sentence}'")
        print(f"    tokens ({len(tokens)}): {tokens}")
        print(f"    decoded: '{decoded}'  round trip ok: {round_trip}")

    total_tokens = sum(len(r[1]) for r in results)
    total_words = sum(len(re.findall(r"[a-z]+", r[0].lower())) for r in results)
    print(f"\nTest sentences: {total_tokens} tokens for {total_words} words "
          f"({total_tokens / total_words:.2f} tokens per word)")

    write_report(texts, live, counts, merges, vocab_size, results)


def write_report(texts, live, counts, merges, vocab_size, results,
                 path="tokenizer_report.md"):
    lines = ["# BPE Tokenizer Report", "",
             "Generated by `bpe_tokenizer.py` (Chapter 3). Byte Pair "
             f"Encoding trained from scratch with {NUM_MERGES} merges "
             "(Sennrich et al., 2016).", "",
             f"- **Corpus:** {len(texts)} stories "
             f"({'live TinyStories data' if live else 'FALLBACK SAMPLE, network unavailable'}), "
             f"{sum(counts.values())} words, {len(counts)} unique words",
             f"- **Vocabulary size:** {vocab_size} tokens",
             f"- **Merges learned:** {len(merges)}",
             "",
             "## First 15 merges",
             ""]
    for i, pair in enumerate(merges[:15]):
        lines.append(f"{i + 1}. `{pair[0]}` + `{pair[1]}` -> `{''.join(pair)}`")
    lines.append("")
    lines += ["## Test sentences", ""]
    for sentence, tokens, decoded, ratio, round_trip in results:
        lines.append(f"- \"{sentence}\"")
        lines.append(f"  - tokens ({len(tokens)}): `{tokens}`")
        lines.append(f"  - decoded: \"{decoded}\" (round trip ok: {round_trip})")
    lines.append("")
    lines += [
        "## What this means",
        "",
        "The first merges are the most common letter pairs in the corpus, "
        "usually pieces of the most common words: 'th', 'he', 'ing', 'ed'. "
        "That is the whole trick of BPE. Frequent patterns get short codes, "
        "rare words stay long. The third test sentence shows the safety net: "
        "'xylophone' never appears in TinyStories, so the tokenizer falls "
        "back to small pieces and single letters instead of failing. No "
        "word is ever unrepresentable.",
        "",
        "Tokens per word is the number that matters downstream. A tokenizer "
        "trained on simple stories will split technical or non-English text "
        "into many more pieces, which costs context window and compute. "
        "That is why production models train their tokenizer on the same "
        "kind of data they will train on, and why the tokenizer is part of "
        "the preparation record, not an afterthought.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
