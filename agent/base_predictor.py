# agent/base_predictor.py
from abc import ABC, abstractmethod
from typing import Dict
from llm.llm_client import LLMClient

class BasePredictor(ABC):
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    @abstractmethod
    def predict(self, sample: Dict) -> str:
        pass

    @staticmethod
    def normalize(output: str) -> str:
        output = output.strip().lower()
        if "true" in output:
            return "True"
        if "false" in output:
            return "False"
        return "Uncertain"
