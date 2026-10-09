# agent/ltrag/translate_story_fix_predictor.py
from typing import Dict, List
from agent.base_predictor import BasePredictor
from agent.ltrag.retrieval.story_retriever import StoryRetriever
from agent.ltrag.translation.story_translator import StoryTranslatorRagLLM
from z3_module.reasoner import check_entailment
from agent.ltrag.fixer.rag_fixer import RagFixer
import json


class TranslateStoryFixPredictor(BasePredictor):
    def __init__(self, llm, kb_path: str = "data/translation-kb.json", top_k: int = 1):
        super().__init__(llm)
        self.retriever = StoryRetriever(kb_path)
        self.translator = StoryTranslatorRagLLM()
        self.fixer = RagFixer()
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
            # 1️⃣ Build query và retrieve examples
            query = self.build_query(sample)
            retrieved_examples = self.retriever.retrieve(query, top_k=self.top_k)

            # 2️⃣ Translate to FOL
            fol_sample = self.translate_to_fol(sample, retrieved_examples)
            # print("=========== FOL ===========")
            # print(fol_sample)
            # print("=========== FOL ===========")
        except Exception as e:
            print(f"[ERROR] Translation/Retrieval failed: {e}")
            return "Uncertain"

        # 3️⃣ Set up max attempts (include premises + conclusion)
        max_attempts = len(fol_sample["premises-FOL"]) + 1
        attempt = 0
        result = "Uncertain"

        while attempt < max_attempts:
            try:
                # 4️⃣ Check entailment
                result = check_entailment(fol_sample["premises-FOL"], fol_sample["conclusion-FOL"])
                print("=== Parsing successfully ===")
                return result  # Nếu thành công, trả ngay
            except Exception as e:
                error_msg = str(e)
                # print(f"[Attempt {attempt+1}] Failed: {error_msg}")

                try:
                    error_dict = json.loads(error_msg)
                except json.JSONDecodeError:
                    print("[WARN] Parser error is not in JSON format:", error_msg)
                    return "Uncertain"

                # 5️⃣ Fix conclusion
                if error_dict.get("index") == -1:
                    fixed_conclusion = self.fixer.fix(
                        fol_error=error_dict["error_line"],
                        error_msg=error_dict["error_msg"],
                        premise=sample['conclusion']
                    )
                    fol_sample['conclusion-FOL'] = fixed_conclusion
                    print("[INFO] Fixed conclusion-FOL")
                    attempt += 1
                    continue

                # 6️⃣ Fix premise
                idx = error_dict.get("index")
                if not isinstance(idx, int) or not (0 <= idx < len(fol_sample["premises-FOL"])):
                    print(f"[WARN] Invalid premise index: {idx}")
                    return "Uncertain"

                fixed_premise = self.fixer.fix(
                    fol_error=error_dict["error_line"],
                    error_msg=error_dict["error_msg"],
                    premise=sample['premises'][idx] if 0 <= idx < len(sample['premises']) else ""  # dùng đúng premise gốc
                )
                # fol_sample['premises-FOL'][idx] = fixed_premise
                # print(f"[INFO] Fixed premise-FOL at index {idx}")
                attempt += 1
                # print("Current FOL sample:", fol_sample)

        # Nếu hết số lần fix mà vẫn lỗi
        # print("[WARN] Maximum attempts reached, returning 'Uncertain'")
        return "Uncertain"


    # def predict(self, sample: Dict) -> str:
    #     try:
    #         query = self.build_query(sample)
    #         # print(query)
    #         retrieved_examples = self.retriever.retrieve(query, top_k=self.top_k)
            
    #         fol_sample = self.translate_to_fol(sample, retrieved_examples)
    #         print("=========== FOL ===========")
    #         print(fol_sample)
    #         print("=========== FOL ===========")
    #     except Exception as e:
    #         result = "Uncertain"
    #         print(f"Error: {e}")

    #     max_attempts = len(fol_sample["premises-FOL"]) + 1
    #     attempt = 0
    #     result = "Uncertain"
        
    #     while attempt < max_attempts:
    #         try:
    #             # Thử check entailment
    #             result = check_entailment(fol_sample["premises-FOL"], fol_sample["conclusion-FOL"])
    #             print("=== parsing successfully ===")
    #             return result  # Nếu thành công, trả ngay
    #         except Exception as e:
    #             error_msg = str(e)
    #             print(f"Attempt {attempt+1} failed: {error_msg}")
    #             print(" ======== FOL ======== ")
    #             print(fol_sample)
    #             attempt += 1
    #             try:
    #                 error_dict = json.loads(error_msg)
    #             except json.JSONDecodeError:
    #                 print("Parser error is not in JSON format:", error_msg)
    #                 return "Uncertain"
                
    #             # print(error_dict["index"])       # 2
    #             # print(error_dict["error_msg"])   # Expected LPAREN, got ID
    #             # print(error_dict["error_line"])  # ∀animal (IsAnimal(animal) → ...)
    #             # print(error_dict["pointer"])     # pointer string
                
    #             if (error_dict["index"] == -1): # fix conclusion
    #                 # Gọi FixerLLM để sửa conclusion
    #                 fixed_sample = self.fixer.fix(fol_error=error_dict["error_line"], error_msg=error_dict["error_msg"], premise=sample['conclusion'])
    #                 fol_sample['conclusion-FOL']=fixed_sample
                    
    #                 continue
                
    #             # ===== fix premise =====
    #             idx = error_dict.get("index", None)
    #             if not isinstance(idx, int) or not (0 <= idx < len(fol_sample["premises-FOL"])):
    #                 print(f"[WARN] Invalid premise index: {idx}")
    #                 return "Uncertain"
                    
    #             # print("===== Param for fix =======")
    #             # print(sample['premises'][error_dict["index"]])
    #             # print(fol_sample['premises-FOL'][error_dict["index"]])

    #             # Gọi FixerLLM để sửa premises-fol
    #             fixed_sample = self.fixer.fix(fol_error=error_dict["error_line"], error_msg=error_dict["error_msg"], premise=sample['conclusion'])
    #             fol_sample['premises-FOL'][error_dict["index"]] = fixed_sample
    #             print(fol_sample)

    #     # Nếu hết số lần fix mà vẫn lỗi
    #     return "Uncertain"
