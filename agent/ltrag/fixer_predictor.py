# agent/ltrag/fixer_predictor.py
from typing import Dict, List
from agent.ltrag.translate_predictor import TranslatePredictor
from agent.ltrag.fixer.fixer import FixerLLM
from z3_module.reasoner import check_entailment
import json

class FixerPredictor(TranslatePredictor):
    def __init__(self, llm, kb_path: str = "data", top_k: int = 5, fixer_examples: List[Dict] = None):
        super().__init__(llm, kb_path, top_k)
        self.fixer = FixerLLM()
        self.fixer_examples = fixer_examples or []

    def predict(self, sample: Dict) -> str:
        """
        Ghi đè predict để thêm cơ chế fix lỗi lặp tối đa:
        - Thử check entailment
        - Nếu lỗi, fix từng premise hoặc conclusion, tối đa len(premises) lần
        - Nếu vẫn không được, trả "Uncertain"
        """
        fol_sample = self.translate_to_fol(
            sample, 
            # self.retriever.retrieve(self.build_query(sample), top_k=self.top_k)
            []
        )

        # max_attempts = len(fol_sample["premises-FOL"])
        max_attempts = 3
        attempt = 0
        result = "Uncertain"

        while attempt < max_attempts:
            try:
                # Thử check entailment
                result = check_entailment(fol_sample["premises-FOL"], fol_sample["conclusion-FOL"])
                print("=== parsing successfully ===")
                return result  # Nếu thành công, trả ngay
            except Exception as e:
                error_msg = str(e)
                # print(f"Attempt {attempt+1} failed: {error_msg}")
                # print(" ======== FOL ======== ")
                # print(fol_sample)
                
                try:
                    error_dict = json.loads(error_msg)
                except json.JSONDecodeError:
                    print("Parser error is not in JSON format:", error_msg)
                    return "Uncertain"
                
                # print(error_dict["index"])       # 2
                # print(error_dict["error_msg"])   # Expected LPAREN, got ID
                # print(error_dict["error_line"])  # ∀animal (IsAnimal(animal) → ...)
                # print(error_dict["pointer"])     # pointer string
                
                if (error_dict["index"] == -1): # fix conclusion
                    # Gọi FixerLLM để sửa conclusion
                    fixed_sample = self.fixer.fix(
                        original_sample=sample['conclusion'],
                        fol_sample=fol_sample['conclusion-FOL'],
                        error_msg=error_dict["error_msg"],
                    )
                    fol_sample['conclusion-FOL']=fixed_sample
                    attempt += 1
                    continue
                
                # ===== fix premise =====
                idx = error_dict.get("index", None)
                if not isinstance(idx, int) or not (0 <= idx < len(fol_sample["premises-FOL"])):
                    print(f"[WARN] Invalid premise index: {idx}")
                    return "Uncertain"
                    
                # print("===== Param for fix =======")
                # print(sample['premises'][error_dict["index"]])
                # print(fol_sample['premises-FOL'][error_dict["index"]])

                # Gọi FixerLLM để sửa premises-fol
                fixed_sample = self.fixer.fix(
                    original_sample=sample['premises'][error_dict["index"]],
                    fol_sample=fol_sample['premises-FOL'][error_dict["index"]],
                    error_msg=error_dict["error_msg"],
                )
                fol_sample['premises-FOL'][error_dict["index"]] = fixed_sample
                print(fol_sample)
                attempt += 1

        # Nếu hết số lần fix mà vẫn lỗi
        return "Uncertain"
