# agent/ltrag/fixer/fixer.py
from llm.llm_client import LLMClient
from typing import Dict
import json
import re


class FixerLLM:
    """
    Fix syntax errors in FOL formulas based on Z3 error messages.
    """

    def __init__(self):
        self.client = LLMClient()

        self.rule_msg = """You must strictly follow the grammar of the first-order logic (FOL):

Allowed logical operators:
1) Conjunction: expr1 ∧ expr2
2) Disjunction: expr1 ∨ expr2
3) Exclusive disjunction: expr1 ⊕ expr2
4) Negation: ¬expr
5) Implication: expr1 → expr2
6) Biconditional: expr1 ↔ expr2
7) Universal quantifier: ∀x
8) Existential quantifier: ∃x

Allowed variables: u, v, w, x, y, z

Invalid characters (MUST NOT appear): ∈, ∉, =, ≠, ≤, ≥, <, >, True, False

Do NOT use equality or comparison symbols.
Use predicates instead.
"""

        self.output_msg = """Output format rules (STRICT):
- Output MUST be an FOL
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include extra text
Output example: ∀x (Emmet(x) ↔ Blake(x))
"""

        self.fix_msg = """
        COMMON SYNTAX ERRORS AND HOW TO FIX THEM:

1) Nested predicates (predicate inside another predicate)
    Example:  A(B(x))
    Fix:
     - Flatten predicates
     - Introduce a new predicate if needed
    Output:
       A(B(x))  →  B(x) ∧ A(x)

3) Missing or extra parentheses
    Example:  ∀x A(x → B(x)
    Fix:
     - Ensure every '(' has a matching ')'
     - Parentheses must reflect logical structure
    Output:
      ∀x A(x) → B(x)

4) Using commas to separate predicates instead of logical operators
    Example:  A(x), B(x)
    Fix:
     - Replace with logical conjunction
    Output:
       A(x) ∧ B(x)

5) Numeric constants used as identifiers
    Example:  HeldIn(1976, montreal)
    Fix:
     - Convert numeric constants into symbolic identifiers
    Output:
       HeldIn(y1976, montreal)

6) Invalid characters
    Example:  x = winter 
    Fix:
     - Remove the invalid characters
    Output:
       Winter(x)
       
IMPORTANT:
- Apply these fixes ONLY when necessary
- Do NOT introduce new predicates unless required to fix syntax
- Do NOT change the original logical meaning
        """

    def _extract_json(self, text: str) -> Dict:
        """
        Robust JSON extraction in case LLM wraps output with text.
        """
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in LLM response")
        return json.loads(match.group())

    def fix(self, original_sample: str, fol_sample: str, error_msg: str) -> Dict:
        """
        Fix FOL syntax errors using LLM.
        """
        
        prompt = "Fix the syntax First-Order Logic below:"
        
        prompt += f"""
        BROKEN_FOL:{fol_sample}\n
        ORIGINAL_PREMISES: {original_sample}\n
        ERROR_MESSAGE: {error_msg}\n
        """
        rule = (
            "SOME CRITICAL RULES:\n"
            + self.rule_msg + "\n\n"
            + self.fix_msg + "\n\n"
            + self.output_msg
            # "OUTPUT EXAMPLE (FOLLOW EXACTLY):\n"
            # "∀x (Emmet(x) ↔ Blake(x))"
        )
        prompt += rule
        
        # print("====== PROMPT =======")
        # print(prompt)
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a compiler backend that outputs corrected First-Order Logic programs.\n"
                    "You receive a First-Order Logic program with its natural language premise and an error message.\n"
                    "Your task is ONLY to fix **syntax errors** in the FOL formula so that it can be parsed. Do NOT modify the meaning, do NOT add new predicates, do NOT add explanations."
                )
            }
            ,
            {
                "role": "user",
                "content": prompt
            }
        ]
        response = self.client.chat_completion(messages)
        # print("========== Fixed FOL ==========")
        # print(response)
        
        return response
        
        # # print(prompt)
        # try:
        #     response = self.client.chat_completion(messages)
        #     fixed_sample = self._extract_json(response)
        #     print("========== Fixed example ==========")
        #     print(fixed_sample)

        #     # Hard validation
        #     if (
        #         not isinstance(fixed_sample, dict)
        #         or "premises-FOL" not in fixed_sample
        #         or "conclusion-FOL" not in fixed_sample
        #         or not isinstance(fixed_sample["premises-FOL"], list)
        #         or not isinstance(fixed_sample["conclusion-FOL"], str)
        #     ):
                
                
        #         raise ValueError("Invalid JSON schema")

        #     # Ensure number of premises is preserved
        #     if len(fixed_sample["premises-FOL"]) != len(fol_sample["premises-FOL"]):
        #         raise ValueError("Premise count changed")

        #     return fixed_sample

        # except Exception as e:
        #     print(f"[FixerLLM] Failed to fix FOL: {e}")
        #     return fol_sample
