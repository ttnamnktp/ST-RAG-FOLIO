# agent/ltrag/translate_predictor.py
from typing import Dict, List
from agent.base_predictor import BasePredictor
from agent.ltrag.retrieval.retriever import Retriever
from agent.ltrag.translation.translator import TranslatorLLM
from z3_module.reasoner import check_entailment


class TranslatePredictor(BasePredictor):
    def __init__(self, llm, kb_path: str = "data", top_k: int = 5):
        super().__init__(llm)
        self.retriever = Retriever(kb_path)
        self.translator = TranslatorLLM()
        self.top_k = top_k

    def build_query(self, sample: Dict) -> str:
        return " ".join(sample["premises"]) + " Therefore " + sample["conclusion"]

    def translate_to_fol(
        self, sample: Dict, retrieved_examples: List[Dict]
    ) -> Dict:
        """
        TRANSLATE ONCE — WHOLE FOLIO SAMPLE
        """
        fol_sample = self.translator.formalize(sample, retrieved_examples)

        assert "premises-FOL" in fol_sample
        assert "conclusion-FOL" in fol_sample

        return fol_sample

    def predict(self, sample: Dict) -> str:
        try:
            # query = self.build_query(sample)
            # retrieved_examples = self.retriever.retrieve(query, top_k=self.top_k)
            retrieved_examples = [] # tạm thời không retrieve để test

            fol_sample = self.translate_to_fol(sample, retrieved_examples)
    
            result = check_entailment(
                fol_sample["premises-FOL"],
                fol_sample["conclusion-FOL"]
            )
        except Exception as e:
            result = "Uncertain"
            # print("======== Sample ========")
            # print(sample)
            # print("======== FOL ========")
            print(fol_sample)
            print(f"Error: {e}")
        # print("=========== FOL ===========")
        # print(fol_sample)
        # print("=========== FOL ===========")

        return result
