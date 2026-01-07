# data/data_loader.py
import json
from typing import List, Dict

class JsonlDatasetLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Dict]:
        data = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data.append(json.loads(line))
        return data
