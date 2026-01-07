# llm/local_embedder.py
from fastembed import TextEmbedding
import numpy as np

class LocalEmbedder:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        # Model sẽ tự động tải về (~100MB)
        self.model = TextEmbedding(model_name=model_name)
        print(f"Loaded embedding model: {model_name}")
    
    def embed(self, texts):
        """Tạo embedding local miễn phí"""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = list(self.model.embed(texts))
        return np.array(embeddings)