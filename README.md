# YuiAI

YuiAI is a fully local chat + TTS system built for low-latency, CPU-first inference.
No cloud services, no tracking, no external APIs.

- LLM backend: **llama.cpp (HTTP server)**
- TTS backend: **FishSpeech (HTTP)**
- API server: **FastAPI**
- Memory: simple local JSON-based memory
- UI: minimal static HTML + JS

---

## Requirements

### System
- Linux (x86_64)
- Python 3.11
- GCC / CMake (for llama.cpp)
- ~8–16 GB RAM recommended
- RTX 3060 (12GB) or compare Nvidia graphics cards with at least 12GB VRAM for FishSpeech TTS

### Runtime services
You must run **both** services before starting YuiAI:
- llama.cpp server
- FishSpeech API server

---

## Python Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````

---

## llama.cpp Setup

### Build llama.cpp

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
mkdir build && cd build

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_BLAS=ON \
  -DLLAMA_BLAS_VENDOR=OpenBLAS

cmake --build . -j$(nproc)
```

Binaries will be located in:

```
llama.cpp/build/bin/
```

---

### Run llama.cpp Server

Example (CPU, 16 threads):

```bash
./llama-server \
  -m /path/to/model.gguf \
  -t 16 \
  -c 4096 \
  --host 127.0.0.1 \
  --port 8081
```

YuiAI expects the llama.cpp HTTP endpoint at:

```
http://127.0.0.1:8081/completion
```

---

## Model Recommendation

Tested and suitable models (GGUF):

* Qwen2.5-1.5B-Instruct (Q4_K_M)
* Qwen2.5-3B-Instruct (Q4_K_M)
* LLaMA 3.2 3B Instruct (Q4)

Small models are **intentional** for fast, short, conversational replies.

---

## FishSpeech Setup

[Installation instructions](https://speech.fish.audio/install/) and [inference API server instructions](https://speech.fish.audio/inference/) and [repository](https://github.com/fishaudio/fish-speech) from FishSpeech

FishSpeech must expose an HTTP TTS endpoint.

Expected endpoint:

```
http://127.0.0.1:8080/v1/tts
```

The TTS server:

* runs independently
* uses a fixed reference voice
* returns WAV audio

YuiAI communicates with it via `modules/fishspeech_client.py`.

---

## Project Structure

```
.
├─ server.py
├─ modules/
│  ├─ llama_client.py      # llama.cpp HTTP client
│  ├─ fishspeech_client.py # TTS HTTP client
│  └─ memory.py            # local memory handling
├─ webui/
│  └─ index.html
└─ data/
   └─ memory.json
```

---

## Start YuiAI

```bash
python server.py
```

Server runs on:

```
http://localhost:8000
```

---

## API Endpoints

### Chat

```
POST /chat
Body: { "text": "your message" }
```

### Text-to-Speech

```
POST /tts
Body: { "text": "text to speak" }
```

### Memory Debug

```
GET /memory/list
GET /memory/reset
```

---

## Notes

* All inference is **local**
* llama.cpp handles LLM inference
* YuiAI only orchestrates prompt, memory and routing
* Memory is intentionally simple and transparent
* Designed for short, natural, conversational replies

