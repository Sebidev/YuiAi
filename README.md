# YuiAI – Local Chat + TTS System

YuiAI is a fully local AI assistant built with:
- **FastAPI**
- **Qwen2.5 1.5B Instruct** (CPU)
- **XTTS v2** via Podman
- **Local vector memory** using Sentence Transformers  
- **Lightweight WebUI** (HTML + JS)

## Features
- Local chat using Qwen2.5
- Local speech synthesis (XTTS v2 via Podman)
- Lightweight memory system stored on disk
- Simple WebUI with “thinking…” placeholder and TTS playback
- No external APIs required

## Project Structure
```
repo/
├─ server.py
├─ modules/
│  ├─ qwen.py
│  ├─ xtts.py
│  └─ memory.py
├─ webui/
│  └─ index.html
└─ data/
   ├─ memory.json
   └─ embeddings.npy
```

## Running the Server
```bash
cd repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn server:app --host 0.0.0.0 --port 8000
```

## XTTS Requirements
XTTS v2 runs via Podman using:
```bash
podman pull ghcr.io/coqui-ai/tts-cpu
```

You must place:
- `coqui_models/`
- `samples/ref.wav`
- `tts_out/`

in the working directory.

## WebUI
Open:
```
http://localhost:8000
```

## License
MIT License
