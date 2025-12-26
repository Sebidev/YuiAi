# YuiAI

YuiAI is a fully local chat + TTS system focused on low-latency, offline usage.
It is designed for small, fast language models and a simple, transparent memory system.

No cloud APIs.  
No tracking.  
No accounts.

---

## Architecture Overview

YuiAI consists of three independent parts:

1. **FastAPI Server**
   - Orchestrates chat, memory and TTS
2. **LLM Backend**
   - `llama.cpp` running as a local HTTP server
3. **TTS Backend**
   - FishSpeech running as a separate local service

All components communicate via HTTP on localhost.

---

## Requirements

### System
- Linux (x86_64)
- Python 3.11
- CMake + GCC/Clang (for llama.cpp)
- 8–16 GB RAM recommended
- RTX 3060 (12GB) or compare Nvidia graphics cards with at least 12GB VRAM for FishSpeech TTS

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

The binaries will be located in:

```
llama.cpp/build/bin/
```

---

### Run llama.cpp Server

Example:

```bash
./llama-server \
  -m /path/to/model.gguf \
  -t 16 \
  -c 4096 \
  --host 127.0.0.1 \
  --port 8081
```

YuiAI expects the endpoint:

```
http://127.0.0.1:8081/completion
```

---

## Supported / Tested Models (GGUF)

* Qwen2.5-1.5B-Instruct (Q4_K_M)
* Qwen2.5-3B-Instruct (Q4_K_M)
* LLaMA 3.2 3B Instruct (Q4)

Small models are intentional to keep latency low and responses short.

---

## TTS Backend (FishSpeech)

YuiAI does **not** run TTS internally.
It connects to an external FishSpeech server via HTTP.

### FishSpeech Repository

FishSpeech is developed here:

**[https://github.com/fishaudio/fish-speech](https://github.com/fishaudio/fish-speech)**
**[https://speech.fish.audio/](https://speech.fish.audio/)**


Please follow the setup instructions in the FishSpeech repository.

---

### Expected TTS Endpoint

YuiAI expects a TTS endpoint at:

```
http://127.0.0.1:8080/v1/tts
```

* Input: text + reference voice
* Output: WAV audio
* Blocking request (non-streaming)

The integration is implemented in:

```
modules/fishspeech_client.py
```

---

## Project Structure

```
.
├─ server.py
├─ modules/
│  ├─ llama_client.py      # llama.cpp HTTP client
│  ├─ fishspeech_client.py # FishSpeech HTTP client
│  └─ memory.py            # local JSON-based memory
├─ webui/
│  └─ index.html
└─ data/
   └─ memory.json
└─ Voicefiles/
   └─ Ref_Nao.wav # reference voice sample (not included by default)
```
---

## Voice Reference (TTS)

YuiAI uses a fixed reference voice sample for FishSpeech cloning.
The server expects the reference WAV at: voicefiles/Ref_Nao.wav

```bash
mkdir voicefiles
```

And a matching reference transcript inside `modules/fishspeech_client.py`:

- `REF_WAV = Path("voicefiles/Ref_Nao.wav")`
- `REF_TEXT = "<your reference text>"`

### WAV Requirements (recommended)
- Format: WAV (PCM)
- Sample rate: 22.05 kHz or 24 kHz (whatever your FishSpeech setup expects)
- Mono recommended
- Length: ~3–10 seconds clean voice, minimal noise

### Git / Privacy Note

Do **not** commit personal voice samples.
Add this to `.gitignore`:
---

## Running YuiAI

Make sure **both services are running**:

* llama.cpp server
* FishSpeech server

Then start YuiAI:

```bash
python server.py
```

The web UI is available at:

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

## Design Notes

* All inference is local
* llama.cpp handles LLM execution
* YuiAI only manages prompt structure, memory and routing
* Memory is intentionally simple and transparent
* Optimized for short, natural, conversational replies
