# modules/llama_client.py
import requests
import threading
import re

LLAMA_URL = "http://127.0.0.1:8081/completion"
TIMEOUT = 120
LOCK = threading.Lock()

# Entfernt ggf. "ASSISTANT:" / "Antwort:" usw.
_PREFIX_RE = re.compile(r"^\s*(ASSISTANT:|Antwort:)\s*", re.IGNORECASE)

def llama_chat(prompt: str) -> str:
    if not LOCK.acquire(blocking=False):
        raise RuntimeError("LLAMA busy")

    try:
        payload = {
            "prompt": prompt,
            "n_predict": 120,          # bisschen Luft, aber kurz durch Prompt
            "temperature": 0.65,
            "top_p": 0.9,
            "repeat_penalty": 1.2,

            # Wichtig: stoppe an klaren Rollenmarkern, NICHT an "\n\n"
            "stop": ["\nUSER:", "\nSYSTEM:", "\nASSISTANT:"],
        }

        resp = requests.post(LLAMA_URL, json=payload, timeout=TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(resp.text)

        data = resp.json()
        text = data.get("content", "").strip()

        # Prefixe entfernen
        text = _PREFIX_RE.sub("", text).strip()

        # Notbremse: nur den ersten Absatz behalten (kleine Modelle schwurbeln sonst)
        text = text.split("\n\n")[0].strip()

        # Notbremse 2: falls er doch Rollenmarker reinschreibt
        for s in ["\nUSER:", "\nSYSTEM:", "\nASSISTANT:"]:
            if s in text:
                text = text.split(s, 1)[0].strip()

        return text

    finally:
        LOCK.release()
