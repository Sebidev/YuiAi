# server.py

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from modules.qwen import qwen_chat
from modules.xtts import generate_tts
from modules.memory import (
    load_memory,
    add_memory,
    get_relevant_memories,
    reset_memory,
    list_memory
)

import io
import os

app = FastAPI()


# ------------------------------------------------------------
# SERVER STARTUP
# ------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    print("[SERVER] Starte…")
    load_memory()
    print("[SERVER] Memory geladen.")


# ------------------------------------------------------------
# MEMORY → Prompt Builder
# ------------------------------------------------------------
def build_prompt_with_memory(user_text: str):
    """Baut den finalen Qwen-Prompt mit Memory-Injektion."""

    memories = get_relevant_memories(user_text)

    memory_block = ""
    if memories:
        memory_block = "Here are things I remember about you:\n"
        for m in memories:
            memory_block += f"- {m}\n"

    system_msg = (
        "Du bist YuiAI, eine freundliche KI-Assistentin. "
        "Bitte antworte immer auf Deutsch, außer der Nutzer spricht ausdrücklich eine andere Sprache."
    )

    # OFFIZIELLES QWEN CHAT FORMAT
    prompt = (
        f"<|im_start|>system\n"
        f"{system_msg}\n"
        f"{memory_block}"
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"{user_text}\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    return prompt


# ------------------------------------------------------------
# CHAT ENDPOINT (fertig & perfekt)
# ------------------------------------------------------------
@app.post("/chat")
async def chat_api(req: dict):
    text = req.get("text", "").strip()
    if not text:
        return {"ok": False, "error": "no_text"}

    # 1. Prompt bauen
    prompt = build_prompt_with_memory(text)

    # 2. LLM antworten lassen
    reply = qwen_chat(prompt)

    # 3. Memory speichern (sehr simpel)
    lower = text.lower()

    # NICHT merken, wenn Reset gerade ausgeführt wurde
    if lower.startswith("!reset"):
        return {"ok": True, "reply": "Memory wurde zurückgesetzt."}

    # Keine Duplicate speichern
    memories = get_relevant_memories(text)
    if memories and text in memories:
        print("[MEMORY] Duplicate → wird nicht gespeichert.")
    else:
        # Nur echte persönliche Aussagen speichern
        if any(k in lower for k in ["ich", "mein", "meine", "mir"]):
            add_memory(text)
            print("[MEMORY] Saved:", text)


    return {"ok": True, "reply": reply}


# ------------------------------------------------------------
# TTS ENDPOINT
# ------------------------------------------------------------
@app.post("/tts")
async def tts_api(req: dict):
    text = req.get("text", "").strip()
    if not text:
        return Response(status_code=400)

    audio_bytes = generate_tts(text)
    if audio_bytes is None:
        return Response(status_code=500)

    # Wir nutzen jetzt BytesIO statt einer Datei
    audio_stream = io.BytesIO(audio_bytes)
    audio_stream.seek(0)

    return StreamingResponse(
        audio_stream,
        media_type="audio/wav",
        headers={
            "Content-Disposition": 'inline; filename="speech.wav"'
        }
    )

# ------------------------------------------------------------
# MEMORY DEBUG ENDPOINTS
# ------------------------------------------------------------
@app.get("/memory/list")
def mem_list():
    mem = list_memory()
    return {"count": len(mem), "items": mem}


@app.get("/memory/reset")
def mem_reset():
    reset_memory()
    return {"ok": True, "msg": "memory cleared"}


# ------------------------------------------------------------
# WEBUI (index.html)
# ------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    path = os.path.join(os.path.dirname(__file__), "webui/index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    return html
