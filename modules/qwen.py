# qwen.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

print("[QWEN] Lade Tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("[QWEN] Lade Modell (CPU only)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    device_map="cpu"
)
print("[QWEN] Modell vollständig geladen.")

STOP_TOKENS = [
    "<|im_end|>",
    "<|im_start|>user",
    "<|im_start|>system"
]


def clean_reply(text: str) -> str:
    """Bereinigt Qwen-Ausgabe"""

    # Assistant-Tag entfernen
    if "<|im_start|>assistant" in text:
        text = text.split("<|im_start|>assistant", 1)[-1]

    # End-Tags entfernen
    for stop in STOP_TOKENS:
        text = text.replace(stop, "")

    return text.strip()


def qwen_chat(prompt: str) -> str:
    """Generate Antwort von Qwen2.5"""

    tokens = tokenizer(prompt, return_tensors="pt").to(model.device)

    output = model.generate(
        **tokens,
        max_new_tokens=512,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        eos_token_id=tokenizer.eos_token_id
    )

    decoded = tokenizer.decode(output[0], skip_special_tokens=False)
    return clean_reply(decoded)
