# fishspeech_client.py
import threading
import requests
import ormsgpack
from pathlib import Path

FISHSPEECH_URL = "http://127.0.0.1:8080/v1/tts"
TIMEOUT = (5, 300)
LOCK = threading.Lock()

# 🔒 FESTE Yui-Stimme (SERVERSEITIG)
REF_WAV = Path("voicefiles/Ref_Nao.wav")
REF_TEXT = "ん?あ、なんかすごく飲みやすい赤ワインですね。"

def generate_tts(text: str) -> bytes:
    if not LOCK.acquire(blocking=False):
        raise RuntimeError("FishSpeech busy")

    try:
        payload = {
            "text": text,
            "references": [{
                "audio": REF_WAV.read_bytes(),
                "text": REF_TEXT,
            }],
            "reference_id": None,
            "format": "wav",
            "max_new_tokens": 1024,
            "chunk_length": 300,
            "top_p": 0.8,
            "repetition_penalty": 1.1,
            "temperature": 0.8,
            "streaming": False,
            "use_memory_cache": "off",
        }

        resp = requests.post(
            FISHSPEECH_URL,
            params={"format": "msgpack"},
            data=ormsgpack.packb(payload),
            headers={"content-type": "application/msgpack"},
            timeout=TIMEOUT,
        )

        if resp.status_code != 200:
            raise RuntimeError(resp.text)

        return resp.content

    finally:
        LOCK.release()
