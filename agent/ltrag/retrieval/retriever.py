# agent/ltragretrieval/retriever.py
import numpy as np
import faiss
import os
from llm.local_embedder import LocalEmbedder
from data.data_loader import JsonlDatasetLoader


class Retriever:
    def __init__(self, kb_path: str):
        self.kb_path = kb_path
        self.embedder = LocalEmbedder()
        self.index = None
        self.examples = []
        self.load_kb()

    def load_kb(self):
        """
        Load FOLIO train set từ jsonl
        """
        example_file = os.path.join(self.kb_path, "folio-train.jsonl")
        emb_file = os.path.join(self.kb_path, "embeddings.npy")

        print("Loading KB from:", example_file)

        if not os.path.exists(example_file):
            print(f"Warning: No KB found at {example_file}")
            return

        # ✅ Load jsonl 
        loader = JsonlDatasetLoader(example_file)
        self.examples = loader.load()

        # ✅ Build text field nếu chưa có
        texts = []
        for ex in self.examples:
            if "text" not in ex:
                premises_fol = " ".join(ex.get("premises-FOL", []))
                premises_nl = " ".join(ex.get("premises", []))
                conclusion = ex.get("conclusion", "")

                ex["text"] = (
                    f"{premises_nl} "
                    f"[FOL] {premises_fol} "
                    f"Therefore {conclusion}"
                )
                
            texts.append(ex["text"])

        # Load / build embeddings
        if os.path.exists(emb_file):
            embeddings = np.load(emb_file)
        else:
            embeddings = self.embedder.embed(texts)
            np.save(emb_file, embeddings)

        # Build FAISS index
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype("float32"))

        print(f"KB loaded: {len(self.examples)} examples")

    def retrieve(self, query: str, top_k: int = 5):
        if self.index is None:
            return []

        query_embedding = self.embedder.embed([query])
        distances, indices = self.index.search(
            query_embedding.astype("float32"), top_k
        )

        results = []
        for idx in indices[0]:
            if idx < len(self.examples):
                results.append(self.examples[idx])

        return results
