# agent/ltrag/retrieval/story_retriever.py
import json
import os
import numpy as np
from collections import defaultdict
from llm.local_embedder import LocalEmbedder


class StoryRetriever:
    """
    Retrieve by STORY-level similarity (story ↔ story).
    """

    def __init__(self, kb_path: str, embed_model="BAAI/bge-small-en-v1.5"):
        self.kb_path = kb_path
        self.embed_path = kb_path + ".story_embeddings.npy"
        self.embedder = LocalEmbedder(model_name=embed_model)

        self.stories = {}          # story_id -> list of entries
        self.story_texts = {}      # story_id -> concatenated text
        self.story_embeddings = {} # story_id -> vector

        self._load_and_build()

    def _load_and_build(self):
        print(f"Loading KB from {self.kb_path} ...")
        with open(self.kb_path, "r", encoding="utf-8") as f:
            entries = json.load(f)

        grouped = defaultdict(list)
        for e in entries:
            story_id = e["id"].rsplit("_p", 1)[0]
            grouped[story_id].append(e)

        self.stories = dict(grouped)

        # build story texts
        for sid, ents in self.stories.items():
            self.story_texts[sid] = " ".join(e["sentence"] for e in ents)

        # load / compute embeddings
        if os.path.exists(self.embed_path):
            print("Loading cached story embeddings...")
            data = np.load(self.embed_path, allow_pickle=True).item()
            self.story_embeddings = data
        else:
            print("Computing story embeddings...")
            for sid, text in self.story_texts.items():
                emb = self.embedder.embed(text)
                self.story_embeddings[sid] = emb[0]
            np.save(self.embed_path, self.story_embeddings)

        print(f"{len(self.stories)} stories ready.")

    def retrieve(self, query_story: str, top_k: int = 3):
        """
        query_story = {
            "premises": [...],
            "conclusion": "..."
        }
        """
        query_emb = self.embedder.embed(query_story)[0]
        query_emb /= np.linalg.norm(query_emb)

        scores = []
        for sid, emb in self.story_embeddings.items():
            emb = emb / np.linalg.norm(emb)
            sim = float(np.dot(query_emb, emb))
            scores.append((sid, sim))

        scores.sort(key=lambda x: -x[1])

        results = []
        for sid, score in scores[:top_k]:
            results.append({
                "story_id": sid,
                "score": score,
                "entries": self.stories[sid]
            })

        return results
