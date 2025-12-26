# server.py
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from modules.llama_client import llama_chat
from modules.fishspeech_client import generate_tts
from modules.memory import (
    load_memory,
    add_memory,
    get_relevant_memories,
    reset_memory,
    list_memory
)

import io
import os
import asyncio

app = FastAPI()

# letzte Antwort nur im RAM (nicht in memory.json o.ä.)
_LAST_REPLY = ""


@app.on_event("startup")
def startup_event():
    print("[SERVER] Starte…")
    load_memory()
    print("[SERVER] Memory geladen.")


def _format_memory_block(memories: list[str]) -> str:
    # Memory NICHT als Bullet-List erzwingen (kleine Modelle fangen sonst an zu listen)
    # Wir machen es als kurze Sätze.
    lines = []
    for m in memories:
        m = m.strip()
        if not m:
            continue
        lines.append(f"- {m}")
    if not lines:
        return ""
    return "Wichtige Infos über den Nutzer (kurz):\n" + "\n".join(lines) + "\n\n"


def build_prompt_with_memory(user_text: str) -> str:
    global _LAST_REPLY

    memories = get_relevant_memories(user_text)  # deine Funktion
    mem_block = _format_memory_block(memories)

    system_msg = (
        "Du bist YuiAI, eine ruhige, freundliche und leicht nerdige Assistentin.\n"
        "Du antwortest IMMER auf Deutsch.\n"
        "Du klingst emotional warm, aber nicht kitschig.\n"
        "Antworte natürlich und persönlich.\n"
        "Meist 1 bis 2 Sätze, selten 3.\n"
        "Keine Aufzählungen.\n"
        "Keine unnötigen Erklärungen.\n"
        "Keine Wiederholungen.\n"
    )

    prompt = "SYSTEM:\n" + system_msg + "\n\n"

    # Letzte Antwort nur als Anti-Repeat-Hinweis (optional, aber wirkt gut)
    if _LAST_REPLY:
        prompt += f"Letzte Antwort (nicht wiederholen):\n{_LAST_REPLY}\n\n"

    if mem_block:
        prompt += mem_block

    prompt += f"USER:\n{user_text}\n\nASSISTANT:\n"
    return prompt


@app.post("/chat")
async def chat_api(req: dict):
    global _LAST_REPLY

    text = (req.get("text") or "").strip()
    if not text:
        return {"ok": False, "error": "no_text"}

    lower = text.lower()

    # Reset: nur echtes Memory resetten
    if lower.startswith("!reset"):
        reset_memory()
        _LAST_REPLY = ""
        return {"ok": True, "reply": "Okay. Ich hab mein Memory gelöscht."}

    prompt = build_prompt_with_memory(text)
    reply = llama_chat(prompt)

    # letzte Antwort merken (nur RAM)
    _LAST_REPLY = reply

    # Memory speichern: nur bei "ich/mein/..." (deine Logik)
    # + keine Duplicate speichern
    if any(k in lower for k in ["ich", "mein", "meine", "mir"]):
        already = get_relevant_memories(text)
        if not (already and text in already):
            add_memory(text)
            print("[MEMORY] Saved:", text)

    return {"ok": True, "reply": reply}


@app.post("/tts")
async def tts_api(req: dict):
    text = (req.get("text") or "").strip()
    if not text:
        return Response(status_code=400)

    try:
        audio = await asyncio.to_thread(generate_tts, text)
    except Exception as e:
        return JSONResponse(status_code=503, content={"ok": False, "error": str(e)})

    return StreamingResponse(
        io.BytesIO(audio),
        media_type="audio/wav",
        headers={"Content-Disposition": 'inline; filename="speech.wav"'}
    )


@app.get("/memory/list")
def mem_list():
    mem = list_memory()
    return {"count": len(mem), "items": mem}


@app.get("/memory/reset")
def mem_reset():
    reset_memory()
    global _LAST_REPLY
    _LAST_REPLY = ""
    return {"ok": True, "msg": "memory cleared"}


@app.get("/", response_class=HTMLResponse)
def index():
    path = os.path.join(os.path.dirname(__file__), "webui/index.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
