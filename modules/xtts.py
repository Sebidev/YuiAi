#!/usr/bin/env python3
import subprocess
import os
import threading

LOCK = threading.Lock()
OUTPUT = "tts_out/output.wav"

def generate_tts(text: str) -> bytes:
    if not LOCK.acquire(blocking=False):
        print("[XTTS] BUSY → Auftrag abgewiesen.")
        return None

    try:
        print("\n================ XTTS DEBUG ================")
        print("[XTTS] Eingabetext:", text)

        # Alte Datei löschen
        try:
            os.remove(OUTPUT)
            print("[XTTS] Alte output.wav gelöscht")
        except FileNotFoundError:
            print("[XTTS] Keine alte output.wav vorhanden")

        cmd = [
            "podman", "run", "--rm",
            "-u", "root",
            "-e", "COQUI_TOS_AGREED=1",
            "-e", "COQUI_TTS_LICENSE=1",
            "-v", "./coqui_models:/root/.local/share/tts",
            "-v", "./samples:/samples",
            "-v", "./tts_out:/data",
            "ghcr.io/coqui-ai/tts-cpu",
            "--model_name", "tts_models/multilingual/multi-dataset/xtts_v2",
            "--text", text,
            "--speaker_wav", "/samples/ref.wav",
            "--language_idx", "de",
            "--out_path", "/data/output.wav"
        ]

        print("[XTTS] Starte Podman:")
        print("       ", " ".join(cmd))

        ret = subprocess.run(cmd, check=False)
        print("[XTTS] Podman return code:", ret.returncode)

        if ret.returncode != 0:
            print("[XTTS] FEHLER: Podman Rückgabecode != 0")
            return None

        if not os.path.exists(OUTPUT):
            print("[XTTS] FEHLER: Keine output.wav erzeugt!")
            return None

        print("[XTTS] SUCCESS → output.wav erzeugt.")
        print("=============================================\n")

        with open(OUTPUT, "rb") as f:
            return f.read()

    finally:
        LOCK.release()
