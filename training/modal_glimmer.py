"""QLoRA fine-tune Muse Glimmer 30B on Modal, then serve the tuned model (partner-provided infrastructure).

  modal run training/modal_glimmer.py::download          # one-time: weights -> Modal volume (CPU, cheap)
  modal run training/modal_glimmer.py::train --steps 10  # smoke test
  modal run training/modal_glimmer.py::train             # full run
  modal run training/modal_glimmer.py::evaluate          # triage accuracy on val set
Weights: meta-models/Muse-Glimmer-30B (Apache-2.0). Data: training/data/*.jsonl (built by build_data.py).
"""
import json
from pathlib import Path

import modal

HF_ID = "meta-models/Muse-Glimmer-30B"
app = modal.App("redflag-glimmer")
vol = modal.Volume.from_name("redflag-glimmer-vol", create_if_missing=True)
VOL = "/vol"

image = (modal.Image.debian_slim(python_version="3.12")
         .pip_install("torch==2.8.0", "transformers==5.21.0", "peft==0.21.2", "bitsandbytes==0.50.2",
                      "accelerate", "huggingface_hub", "hf_transfer", "sentencepiece", "pillow")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": f"{VOL}/hf"})
         .add_local_dir(str(Path(__file__).parent / "data"), "/data"))


@app.function(image=image, volumes={VOL: vol}, timeout=3600)
def download():
    from huggingface_hub import snapshot_download
    p = snapshot_download(HF_ID, local_dir=f"{VOL}/glimmer")
    vol.commit()
    print("downloaded to", p)


def _load(quant=True):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    tok = AutoTokenizer.from_pretrained(f"{VOL}/glimmer")
    kw = dict(device_map={"": 0}, dtype=torch.bfloat16)
    if quant:
        kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                       bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    try:
        model = AutoModelForCausalLM.from_pretrained(f"{VOL}/glimmer", **kw)
    except Exception as e:  # multimodal class fallback
        print("CausalLM load failed, trying ImageTextToText:", type(e).__name__, str(e)[:200])
        from transformers import AutoModelForImageTextToText
        model = AutoModelForImageTextToText.from_pretrained(f"{VOL}/glimmer", **kw)
    return tok, model


def _encode(tok, row, max_len=768):
    msgs = row["messages"]
    prompt_ids = tok.apply_chat_template(msgs[:-1], add_generation_prompt=True, tokenize=True)
    if isinstance(prompt_ids, dict):
        prompt_ids = prompt_ids["input_ids"]
    comp_ids = tok(msgs[-1]["content"] + (tok.eos_token or ""), add_special_tokens=False)["input_ids"]
    ids = (list(prompt_ids) + comp_ids)[:max_len]
    labels = ([-100] * len(prompt_ids) + comp_ids)[:max_len]
    return ids, labels


@app.function(image=image, volumes={VOL: vol}, gpu="A100-80GB", timeout=7200)
def train(steps: int = -1, epochs: int = 2, lr: float = 2e-4, bs: int = 8):
    import random
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    tok, model = _load(quant=True)
    print("model class:", type(model).__name__)
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules="all-linear",
                     exclude_modules=r".*(vision|visual|perception|vit|encoder|projector|lm_head).*", task_type="CAUSAL_LM")
    model = get_peft_model(model, cfg)
    model.print_trainable_parameters()

    rows = [json.loads(l) for l in open("/data/train.jsonl")]
    data = [_encode(tok, r) for r in rows]
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr, weight_decay=0.0)
    total = (len(data) // bs) * epochs if steps < 0 else steps
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 10) * max(0.05, 1 - s / max(1, total)))
    model.train()
    step, rnd = 0, random.Random(0)
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    for ep in range(epochs):
        rnd.shuffle(data)
        for i in range(0, len(data) - bs + 1, bs):
            batch = data[i:i + bs]
            L = max(len(x[0]) for x in batch)
            ids = torch.tensor([x[0] + [pad] * (L - len(x[0])) for x in batch]).cuda()
            lab = torch.tensor([x[1] + [-100] * (L - len(x[1])) for x in batch]).cuda()
            att = torch.tensor([[1] * len(x[0]) + [0] * (L - len(x[0])) for x in batch]).cuda()
            loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); opt.zero_grad()
            step += 1
            if step % 10 == 0 or step == 1:
                print(f"step {step}/{total} loss {loss.item():.4f}", flush=True)
            if step >= total:
                break
        if step >= total:
            break
    out = f"{VOL}/lora-triage" + ("-smoke" if steps > 0 else "")
    model.save_pretrained(out)
    tok.save_pretrained(out)
    vol.commit()
    print("saved adapter to", out)


@app.local_entrypoint()
def main():
    print("use ::download, ::train, ::evaluate")
