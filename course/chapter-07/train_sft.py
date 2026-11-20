"""Chapter 7: QLoRA SFT of TinyLlama-1.1B on Colab (free T4 GPU).

What this does:
  1. Loads the TinyLlama 1.1B BASE model in 4-bit (QLoRA) and freezes it.
  2. Trains small LoRA adapters on sft_data.jsonl (40 instruction pairs).
     The loss is computed only on the response tokens, not the prompt.
  3. Generates answers to the 10 held-out test prompts twice: once with
     the base model, once with the SFT adapter. Same prompts, same
     decoding (greedy), so the difference is the training, not the setup.
  4. Writes generations.json for rubric.py to score.

Run on Colab (see README section 8 for setup):
  !python train_sft.py
  !python train_sft.py --generate-only     (re-run generation only,
                                             after a disconnect)

This script needs a GPU. It stops with a clear message on CPU.
"""

import argparse
import json

import torch
import transformers
import trl
import peft

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T"
DATA_FILE = "sft_data.jsonl"
TEST_FILE = "test_prompts.jsonl"
ADAPTER_DIR = "./sft-out/adapter"

# The format the model sees. This is a convention, not something built
# into the model: the training data teaches it that text after
# "### Response:" is the answer. Keep the format identical in training
# and in generation, or the model will not recognize the task.
INSTRUCTION_TEMPLATE = "### Instruction:\n{prompt}\n\n### Response:\n"


def format_example(prompt, completion):
    return (INSTRUCTION_TEMPLATE.format(prompt=prompt)
            + completion + "\n")


def load_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_dataset():
    """Prompt/completion pairs. TRL masks the prompt tokens, so the
    loss is computed on the completion only. That is the SFT idea
    from sft_loss_demo.py, at real scale."""
    from datasets import Dataset
    rows = load_rows(DATA_FILE)
    return Dataset.from_list([
        {"prompt": INSTRUCTION_TEMPLATE.format(prompt=r["prompt"]),
         "completion": r["completion"]}
        for r in rows
    ])


def load_base():
    """Base model in 4-bit. 1.1B parameters: 2.2 GB at 16-bit, about
    0.55 GB at 4-bit, which is why this fits on a free T4."""
    from transformers import AutoModelForCausalLM, AutoTokenizer, \
        BitsAndBytesConfig
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        attn_implementation="sdpa",
    )
    model.config.use_cache = False
    return model, tokenizer


def train():
    from peft import LoraConfig
    from trl import SFTConfig, SFTTrainer

    model, tokenizer = load_base()
    dataset = build_dataset()
    print(f"Training examples: {len(dataset)}")

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )
    sft_config = SFTConfig(
        output_dir="./sft-out",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        logging_steps=5,
        save_strategy="no",
        max_length=512,
        packing=False,
        completion_only_loss=True,
        report_to="none",
        bf16=True,
    )
    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=dataset,
        peft_config=lora_config,
        processing_class=tokenizer,
    )
    trainer.train()
    trainer.save_model(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)
    print(f"Adapter saved to {ADAPTER_DIR}")
    return model, tokenizer


def generate(model, tokenizer, prompts):
    """Greedy decoding: always the highest-probability token. Same
    choice as Chapter 6, for the same reason: a repeatable number."""
    model.eval()
    outputs = []
    for prompt in prompts:
        text = INSTRUCTION_TEMPLATE.format(prompt=prompt)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_tokens = generated[0][inputs["input_ids"].shape[1]:]
        outputs.append(tokenizer.decode(new_tokens,
                                        skip_special_tokens=True).strip())
    return outputs


def generate_both():
    """Base vs SFT on the same prompts, same decoding."""
    test = load_rows(TEST_FILE)
    prompts = [t["prompt"] for t in test]

    model, tokenizer = load_base()
    base_outputs = generate(model, tokenizer, prompts)
    print("Base generations done.")

    from peft import PeftModel
    model = PeftModel.from_pretrained(model, ADAPTER_DIR)
    sft_outputs = generate(model, tokenizer, prompts)
    print("SFT generations done.")

    generations = []
    for item, base, sft in zip(test, base_outputs, sft_outputs):
        generations.append({
            "id": item["id"],
            "prompt": item["prompt"],
            "category": item["category"],
            "base_output": base,
            "sft_output": sft,
        })
    with open("generations.json", "w") as f:
        json.dump({"generations": generations}, f, indent=2)
    print("Wrote generations.json")

    print("\nSide by side (first 3 prompts):")
    for item in generations[:3]:
        print(f"\n[{item['id']}] {item['prompt']}")
        print(f"  BASE: {item['base_output'][:300]}")
        print(f"  SFT:  {item['sft_output'][:300]}")
    return generations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-only", action="store_true",
                        help="skip training, generate from saved adapter")
    args = parser.parse_args()

    print(f"transformers {transformers.__version__}, "
          f"trl {trl.__version__}, peft {peft.__version__}")
    if not torch.cuda.is_available():
        print("No GPU found. This script trains on Colab (free T4). "
              "Run sft_loss_demo.py, dataset_checks.py, and rubric.py "
              "locally instead; they need no GPU.")
        return

    if not args.generate_only:
        model, tokenizer = train()
        del model, tokenizer
        torch.cuda.empty_cache()
    generate_both()
    print("\nNext: !python rubric.py --generations generations.json")


if __name__ == "__main__":
    main()
