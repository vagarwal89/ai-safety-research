"""Chapter 3 - MinHash near-duplicate detection, from scratch.

Run:  python dedup.py

Needs: pip install datasets   (only for the live TinyStories sample;
      the script falls back to a small embedded sample if the
      download fails, and says so clearly in the report.)

What it does:
  1. Loads a sample of TinyStories (60 stories by default).
  2. Turns each story into a set of word 5-grams ("shingles").
  3. Builds a MinHash signature for each story: 64 hash functions,
     keep the minimum hash of the shingle set under each one.
  4. Estimates Jaccard similarity between every pair of stories
     from their signatures, and checks it against the exact Jaccard.
  5. Reports near-duplicate pairs above a threshold, and how many
     stories a dedup pass would remove.

Why this matters: a training set full of near-copies teaches the model
to memorize instead of generalize, wastes compute on the same text
twice, and can leak test data into training. Dedup is the first gate
in the cleaning pipeline, and it is one of the preparation operations
EU AI Act Article 10(2)(c) names.

Output: dedup_report.md in this folder.
"""

import hashlib
import itertools
from collections import Counter

SHINGLE_SIZE = 5      # words per shingle
NUM_HASHES = 64       # MinHash signature length
THRESHOLD = 0.7       # estimated Jaccard at or above this = near-duplicate
SAMPLE_SIZE = 60

# Small embedded sample, used only when the network is unavailable.
# These are short stories written for this course, not real TinyStories
# rows. Stories 1-4 are planted near-duplicates so you can see the
# method catch them: 2 is an exact copy of 1, 3 changes one word,
# 4 keeps the opening but changes the ending.
FALLBACK_STORIES = [
    "One day, a little girl named Lily found a small red ball in her garden. "
    "She picked it up and threw it high into the sky. The ball came down and "
    "bounced near a big tree. Lily laughed and ran to get it.",
    "One day, a little girl named Lily found a small red ball in her garden. "
    "She picked it up and threw it high into the sky. The ball came down and "
    "bounced near a big tree. Lily laughed and ran to get it.",
    "One day, a little girl named Lily found a small red ball in her yard. "
    "She picked it up and threw it high into the sky. The ball came down and "
    "bounced near a big tree. Lily laughed and ran to get it.",
    "One day, a little girl named Lily found a small red ball in her garden. "
    "She picked it up and threw it high into the sky. Then she gave the ball "
    "to her friend Max and they played together all afternoon.",
    "Once upon a time, there was a little dog named Ben. Ben loved to run in "
    "the park and chase birds. One sunny morning, he found a blue kite stuck "
    "in a bush. He barked happily and wagged his tail.",
    "Tom had a big yellow truck. Every day he drove it to the farm to help his "
    "dad. One day the truck got stuck in the mud. Tom and his dad pushed it "
    "out together.",
    "Sara loved to bake cookies with her mom. They mixed flour and sugar in a "
    "big bowl. The cookies smelled sweet when they came out of the oven. Sara "
    "shared them with her friends at school.",
    "A small fish named Fin lived in a blue pond. He swam with his friends "
    "every morning. One day a big storm made the water cold. Fin hid under a "
    "rock until the sun came back.",
    "Mia found a tiny bird with a hurt wing in her backyard. She put it in a "
    "soft box and gave it water. After two days, the bird could fly again. "
    "Mia watched it fly up into the sky.",
    "Jack had a red kite and a long string. He ran fast across the green "
    "field. The kite flew up high above the trees. Jack smiled and held the "
    "string tight.",
    "Emma planted a seed in a small pot. She watered it every day and put it "
    "near the window. Soon a green plant grew tall. Emma was happy to see a "
    "yellow flower bloom.",
    "A little train named Choo went over the hill. It carried apples to the "
    "town. The people waved as the train passed by. Choo was proud to help "
    "everyone.",
    "Ben and Ana built a tall tower with blocks. The tower fell down with a "
    "crash. They laughed and built it again. This time the tower stayed up "
    "all day.",
    "The moon was bright in the night sky. A little owl sat on a branch and "
    "looked at the stars. It hooted softly and flew home. The owl slept until "
    "the morning sun came up.",
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


def shingles(text, k=SHINGLE_SIZE):
    """A story as a set of word k-grams, lowercased."""
    words = text.lower().split()
    return {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}


def minhash_signature(shingle_set, n=NUM_HASHES):
    """MinHash signature: for each of n hash functions, the minimum
    hash value over the shingle set. Two similar sets get similar
    signatures, because the same shingle tends to win the minimum."""
    signature = []
    for seed in range(n):
        min_value = None
        for item in shingle_set:
            digest = hashlib.md5(f"{seed}:{item}".encode("utf-8")).hexdigest()
            value = int(digest, 16)
            if min_value is None or value < min_value:
                min_value = value
        signature.append(min_value)
    return signature


def exact_jaccard(set_a, set_b):
    """True Jaccard similarity: shared shingles over all shingles."""
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def estimated_jaccard(sig_a, sig_b):
    """Jaccard estimated from MinHash signatures: the fraction of
    positions where the two signatures agree. This estimates the true
    Jaccard, and the estimate gets tighter as NUM_HASHES grows."""
    matches = sum(1 for a, b in zip(sig_a, sig_b) if a == b)
    return matches / len(sig_a)


def find_near_duplicates(texts, threshold=THRESHOLD):
    """Compare every pair. Returns (pairs, signatures, shingle_sets).

    pairs is a list of (i, j, estimated, exact) with estimated Jaccard
    at or above the threshold, sorted by estimated similarity.
    """
    shingle_sets = [shingles(t) for t in texts]
    signatures = [minhash_signature(s) for s in shingle_sets]
    pairs = []
    for i, j in itertools.combinations(range(len(texts)), 2):
        est = estimated_jaccard(signatures[i], signatures[j])
        if est >= threshold:
            exact = exact_jaccard(shingle_sets[i], shingle_sets[j])
            pairs.append((i, j, round(est, 3), round(exact, 3)))
    pairs.sort(key=lambda p: -p[2])
    return pairs, signatures, shingle_sets


def dedup_keep_first(texts, pairs):
    """Keep the first story of each near-duplicate cluster, drop the
    rest. Returns (kept_indices, removed_indices)."""
    removed = set()
    for i, j, _, _ in pairs:
        if i not in removed:
            removed.add(j)
    kept = [i for i in range(len(texts)) if i not in removed]
    return kept, sorted(removed)


def main():
    texts, live = load_stories()
    print(f"Loaded {len(texts)} stories "
          f"({'live TinyStories data' if live else 'FALLBACK SAMPLE, network unavailable'})")
    print(f"Settings: {SHINGLE_SIZE}-gram shingles, {NUM_HASHES} hash functions, "
          f"threshold {THRESHOLD}")

    # Score every pair first (threshold 0), so the report can show the
    # most similar pairs even when nothing clears the threshold.
    all_pairs, signatures, shingle_sets = find_near_duplicates(texts, threshold=0.0)
    pairs = [p for p in all_pairs if p[2] >= THRESHOLD]
    top_pairs = all_pairs[:5]
    kept, removed = dedup_keep_first(texts, pairs)

    print(f"\nNear-duplicate pairs found: {len(pairs)}")
    for i, j, est, exact in pairs[:20]:
        print(f"  stories {i} and {j}: estimated Jaccard {est}, exact {exact}")
    if len(pairs) > 20:
        print(f"  ... and {len(pairs) - 20} more")
    if not pairs:
        print("  Most similar pairs in this sample:")
        for i, j, est, exact in top_pairs:
            print(f"  stories {i} and {j}: estimated Jaccard {est}, exact {exact}")

    print(f"\nDedup pass: kept {len(kept)} of {len(texts)} stories, "
          f"removed {len(removed)} ({100 * len(removed) / len(texts):.1f}%)")

    # How good is the estimate? Compare estimated vs exact on the pairs
    # we found, plus a few random low-similarity pairs.
    errors = [abs(est - exact) for _, _, est, exact in pairs]
    if errors:
        print(f"Estimate error on found pairs: mean {sum(errors) / len(errors):.3f}, "
              f"max {max(errors):.3f}")

    # Sanity check on the fallback sample, so the report is readable
    # even when the live data finds nothing.
    if not live:
        print("\nFallback sample check (planted duplicates):")
        print("  stories 0 and 1 are identical, expect Jaccard 1.0")
        print("  stories 0 and 2 differ by one word, expect high similarity")
        print("  stories 0 and 3 share an opening but differ at the end, "
              "expect lower similarity")

    write_report(texts, live, pairs, top_pairs, kept, removed)


def write_report(texts, live, pairs, top_pairs, kept, removed, path="dedup_report.md"):
    lines = ["# Near-Duplicate Detection Report", "",
             "Generated by `dedup.py` (Chapter 3). MinHash signatures with "
             f"{NUM_HASHES} hash functions over word {SHINGLE_SIZE}-grams; "
             f"near-duplicate threshold {THRESHOLD} estimated Jaccard.", "",
             f"- **Sample:** {len(texts)} stories "
             f"({'live TinyStories data' if live else 'FALLBACK SAMPLE, network unavailable'})",
             f"- **Near-duplicate pairs found:** {len(pairs)}",
             f"- **Dedup pass:** kept {len(kept)} of {len(texts)} stories, "
             f"removed {len(removed)} ({100 * len(removed) / len(texts):.1f}%)",
             ""]
    if pairs:
        lines += ["## Near-duplicate pairs", "",
                  "| story A | story B | estimated Jaccard | exact Jaccard |",
                  "|---|---|---|---|"]
        for i, j, est, exact in pairs:
            lines.append(f"| {i} | {j} | {est} | {exact} |")
        lines.append("")
    else:
        lines += ["No pairs above the threshold in this sample.",
                  "",
                  "## Most similar pairs in this sample",
                  "",
                  "Even with nothing above the threshold, the top pairs show "
                  "how similar the most similar stories are, and how noisy "
                  "the MinHash estimate is at low similarity.",
                  "",
                  "| story A | story B | estimated Jaccard | exact Jaccard |",
                  "|---|---|---|---|"]
        for i, j, est, exact in top_pairs:
            lines.append(f"| {i} | {j} | {est} | {exact} |")
        lines.append("")
        lines += ["Try lowering THRESHOLD in `dedup.py` to see more of the "
                  "similarity distribution, or run it on the fallback sample, "
                  "where duplicates are planted.", ""]
    lines += [
        "## What this means",
        "",
        "Every removed story is text the model would otherwise see twice. "
        "Duplicates do three kinds of harm: they waste training compute, "
        "they push the model toward memorizing the repeated text (Chapter 6 "
        "measures that directly), and if a duplicated story lands in both "
        "training and test data, your evaluation is lying to you. A dedup "
        "pass is cheap insurance against all three.",
        "",
        "The threshold is a judgment call, not a law of nature. Lower it "
        "and you remove more, including stories that are merely similar. "
        "Raise it and near-copies slip through. Record the threshold you "
        "used: it is part of your Article 10(2)(c) preparation record.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
