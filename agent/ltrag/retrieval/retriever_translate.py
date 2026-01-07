# agent/ltrag/retrieval/translation_retriever.py
import json
import os
import numpy as np

from llm.local_embedder import LocalEmbedder

class TranslationRetriever:
    def __init__(self, kb_path: str, embed_model_name: str = "BAAI/bge-small-en-v1.5"):
        self.kb_path = kb_path
        self.embed_path = kb_path + ".embeddings.npy"  # lưu embedding ở cùng folder
        self.embedder = LocalEmbedder(model_name=embed_model_name)
        self.entries = []
        self.embeddings = None
        self._load_kb_and_embeddings()
    
    def _load_kb_and_embeddings(self):
        # Load KB
        print(f"Loading KB from {self.kb_path} ...")
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            self.entries = json.load(f)  # đọc JSON array multi-line
        print(f"{len(self.entries)} entries loaded.")

        # Check nếu đã có file embedding
        if os.path.exists(self.embed_path):
            print(f"Loading cached embeddings from {self.embed_path} ...")
            self.embeddings = np.load(self.embed_path)
        else:
            print("Computing embeddings for KB ...")
            sentences = [e["sentence"] for e in self.entries]
            self.embeddings = self.embedder.embed(sentences)
            np.save(self.embed_path, self.embeddings)
            print(f"Embeddings saved to {self.embed_path}")

    
    def retrieve(self, query: str, top_k: int = 3):
        query_emb = self.embedder.embed(query)  # (1, dim)
        sims = self.embeddings @ query_emb.T
        sims = sims.squeeze() / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb))
        top_idx = np.argsort(-sims)[:top_k]
        return [self.entries[i] for i in top_idx]


# -------------------------
# Example
# -------------------------
if __name__ == "__main__":
    retriever = TranslationRetriever("data/translation-kb.jsonl")
    query = "Where is North Yorkshire?"
    results = retriever.retrieve(query)
    for r in results:
        print("Sentence:", r["sentence"])
        print("FOL:", r["fol_formula"])
        print("Steps:", r["translation_steps"])
        print("----")