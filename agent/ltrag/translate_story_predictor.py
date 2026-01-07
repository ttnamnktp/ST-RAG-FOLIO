# agent/ltrag/translate_rag_predictor.py
from typing import Dict, List
from agent.base_predictor import BasePredictor
from agent.ltrag.retrieval.story_retriever import StoryRetriever
from agent.ltrag.translation.story_translator import StoryTranslatorRagLLM
from z3_module.reasoner import check_entailment


class TranslateStoryPredictor(BasePredictor):
    def __init__(self, llm, kb_path: str = "data/translation-kb.json", top_k: int = 1):
        super().__init__(llm)
        self.retriever = StoryRetriever(kb_path)
        self.translator = StoryTranslatorRagLLM()
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
            query = self.build_query(sample)
            # print(query)
            retrieved_examples = self.retriever.retrieve(query, top_k=self.top_k)
            
            fol_sample = self.translate_to_fol(sample, retrieved_examples)
            print("=========== FOL ===========")
            print(fol_sample)
            print("=========== FOL ===========")
            
            result = check_entailment(
                fol_sample["premises-FOL"],
                fol_sample["conclusion-FOL"]
            )
        except Exception as e:
            result = "Uncertain"
            print(f"Error: {e}")
        

        return result
