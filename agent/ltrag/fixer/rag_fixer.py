# # llm/rag_fixer.py
# import os
# import json
# import numpy as np
# from typing import List, Dict, Optional
# from llm.local_embedder import LocalEmbedder
# from llm.llm_client import LLMClient

# class RagFixer:
#     """
#     A Retrieval-Augmented FOL Fixer that uses KB + LLM to fix FOL formulas.
#     """

#     def __init__(self, kb_path: str, embed_model_name: str = "BAAI/bge-small-en-v1.5"):
#         self.kb_path = kb_path
#         self.embed_path = kb_path + ".embeddings.npy"
#         self.embedder = LocalEmbedder(embed_model_name)
#         self.llm = LLMClient()
#         self.entries = []
#         self.embeddings = None
#         self._load_kb_and_embeddings()

#     def _load_kb_and_embeddings(self):
#         with open(self.kb_path, 'r', encoding='utf-8') as f:
#             self.entries = json.load(f)

#         if os.path.exists(self.embed_path):
#             self.embeddings = np.load(self.embed_path)
#         else:
#             sentences = [
#                 e.get("description", "") + " " + " ".join(e.get("detection_patterns", []))
#                 for e in self.entries
#             ]
#             self.embeddings = self.embedder.embed(sentences)
#             np.save(self.embed_path, self.embeddings)

#     def _retrieve_candidates(self, error_msg: str, error_line: str, top_k: int = 3) -> List[Dict]:
#         query = error_msg + " " + error_line
#         query_emb = self.embedder.embed(query)
#         sims = self.embeddings @ query_emb.T
#         sims = sims.squeeze() / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb))
#         top_idx = sims.argsort()[::-1][:top_k]
#         return [self.entries[i] for i in top_idx]

#     def fix(self, fol_error: str, error_msg: str, premise: Optional[str] = "") -> str:
#         """
#         Input:
#             fol_error: FOL formula bị lỗi
#             error_msg: message lỗi từ parser
#             premise: natural language premise (có thể rỗng)
#         Output:
#             Fixed FOL formula
#         """
#         candidates = self._retrieve_candidates(error_msg, fol_error, top_k=3)

#         # Chuẩn bị prompt cho LLM
#         kb_text = ""
#         for c in candidates:
#             kb_text += f"- Error Type: {c['error_type']}\n"
#             kb_text += f"  Description: {c['description']}\n"
#             rules = c.get('fix_rules', [])
#             if rules:
#                 kb_text += "  Fix Rules:\n"
#                 for r in rules:
#                     kb_text += f"    + {r}\n"
#             else:
#                 kb_text += "  Fix Rules: N/A\n"
#             kb_text += f"  Rewrite Examples: {c.get('rewrite_examples', [])}\n"

#         prompt = f"""
# You are an expert in fixing first-order logic (FOL) formulas.
# Here is a FOL formula with syntax errors:
# {fol_error}

# Error message from parser:
# {error_msg}

# Premises in natural language:
# {premise if premise else 'N/A'}

# Use the following KB of common FOL error patterns and examples to fix it:
# {kb_text}

# Return ONLY the corrected FOL formula. Do not add explanation.
# """
#         print("====== PROMPT ======")
#         print(prompt)
#         response = self.llm.chat_completion([{"role": "user", "content": prompt}])
#         return response



# llm/rag_fixer_basic.py
import json
from typing import Optional
from llm.llm_client import LLMClient

class RagFixer:
    """
    FOL fixer using only the 6 basic errors from KB.
    No retrieval, always considers all 6 errors.
    """

    def __init__(self, kb_path: str = "data/fixer-kb.json"):
        # Load KB
        with open(kb_path, 'r', encoding='utf-8') as f:
            self.entries = json.load(f)
        self.llm = LLMClient()

    def fix(self, fol_error: str, error_msg: str, premise: Optional[str] = "") -> str:
        """
        Input:
            fol_error: FOL formula bị lỗi
            error_msg: message lỗi từ parser
            premise: natural language premise (có thể rỗng)
        Output:
            Fixed FOL formula
        """
        fol_syntax_rules = """
        FOL Syntax Rules:
        1. Predicates must have proper parentheses and correct arity. Format: Predicate(arg1, arg2, ...).
        2. No nested predicates: separate into conjuncts or use implication (e.g., Eat(steve, Dish(fish)) is wrong, should be Eat(steve, fish) ∧ Dish(fish)).
        3. Numeric literals should be replaced with symbolic constants (e.g., 98199 -> zip98199).
        4. Constants cannot appear alone without predicates; attach to a predicate or negate predicate (e.g., steven ∧ Love(steven, connie), steven cannot stand alone like this).
        5. Use only supported logical operators: ∧, ∨, ¬, →, ↔, ⊕, ∀, ∃ (e.g., replace '=' with SameAs(x,y), '>'/'<' with domain-specific predicates).
        6. All parentheses must match: the number of opening '(' must equal the number of closing ')'.
        """

        # Chuẩn bị 6 lỗi cơ bản + fix rules + rewrite examples
        kb_text = ""
        for c in self.entries:
            kb_text += f"- Error Type: {c['error_type']}\n"
            kb_text += f"  Description: {c['description']}\n"

            rules = c.get('fix_rules', [])
            if rules:
                kb_text += "  Fix Rules:\n"
                for r in rules:
                    kb_text += f"    + {r}\n"
            else:
                kb_text += "  Fix Rules: N/A\n"

            examples = c.get('rewrite_examples', [])
            if examples:
                kb_text += "  Rewrite Examples:\n"
                for ex in examples:
                    kb_text += f"    - Before: {ex['before']}\n"
                    kb_text += f"      After:  {ex['after']}\n"
            kb_text += "\n"

        # Tạo prompt
        prompt = f"""
You are an expert in fixing first-order logic (FOL) formulas.

{fol_syntax_rules}

Below are 6 common FOL errors, along with how to fix them and examples:
{kb_text}

Here is a FOL formula with syntax errors:
{fol_error}

Error message from parser:
{error_msg}

Premises in natural language:
{premise if premise else 'N/A'}

Use the information above to fix the formula. 
Return ONLY the corrected FOL formula. Do not add explanation.
"""

        # print("====== PROMPT ======")
        # print(prompt)

        response = self.llm.chat_completion([{"role": "user", "content": prompt}])
        return response

