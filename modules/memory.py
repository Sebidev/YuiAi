import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util

MEMORY_FILE = "data/memory.json"
EMB_FILE = "data/embeddings.npy"

# Lade Modell nur einmal
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Memory-Struktur
memory = []
embeddings = None


def load_memory():
    global memory, embeddings

    # ---- MEMORY.JSON ----
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = f.read().strip()
                if data:
                    memory = json.loads(data)
                else:
                    memory = []
        except Exception:
            print("[MEMORY] WARNUNG: memory.json beschädigt → reset")
            memory = []
    else:
        memory = []

    # ---- EMBEDDINGS ----
    if os.path.exists(EMB_FILE):
        try:
            emb = np.load(EMB_FILE)
            if emb.size > 0:
                embeddings = emb
            else:
                embeddings = np.zeros((0, 384))
        except Exception:
            print("[MEMORY] WARNUNG: embeddings.npy beschädigt → reset")
            embeddings = np.zeros((0, 384))
    else:
        embeddings = np.zeros((0, 384))

    print(f"[MEMORY] Loaded: {len(memory)} items")


def reset_memory():
    """Memory + Embeddings vollständig löschen."""
    global memory, embeddings

    memory = []
    embeddings = np.zeros((0, 384))

    save_memory()

    print("[MEMORY] Reset → OK")


def list_memory():
    return memory


def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

    np.save(EMB_FILE, embeddings)


def add_memory(text: str):
    """Speichert neuen Eintrag + Embedding."""
    global memory, embeddings

    emb = model.encode(text)

    memory.append(text)

    if embeddings is None or len(embeddings) == 0:
        embeddings = np.array([emb])
    else:
        embeddings = np.vstack([embeddings, emb])

    save_memory()


def search_memory(query: str, top_k=3):
    global embeddings

    if embeddings is None or len(embeddings) == 0:
        return []

    query_emb = model.encode(query)
    scores = util.cos_sim(query_emb, embeddings)[0]

    # Prevent crash when memory too small
    k = min(top_k, len(memory))
    if k == 0:
        return []

    top_results = scores.topk(k)

    results = []
    for idx, score in zip(top_results.indices, top_results.values):
        results.append((memory[int(idx)], float(score)))

    return results



def get_relevant_memories(query: str):
    """Gibt NUR Text zurück, ohne Scores."""
    result = search_memory(query)
    return [text for text, _ in result]
