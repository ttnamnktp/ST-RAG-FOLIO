# agent/ltrag/translation/translator.py
from llm.llm_client import LLMClient
from typing import List, Dict
import json


class TranslatorRagLLM:
    def __init__(self):
        self.client = LLMClient()
        self.rule_msg = """The grammar of the first-order logic formular is defined as follows:
1) logical conjunction of expr1 and expr2: expr1 ∧ expr2
2) logical disjunction of expr1 and expr2: expr1 ∨ expr2
3) logical exclusive disjunction of expr1 and expr2: expr1 ⊕ expr2
Things that can't happen at the same time are generally used as logical exclusive disjunction rather than logical disjunction.
4) logical negation of expr1: ¬expr1
5) expr1 implies expr2: expr1 → expr2
6) expr1 if and only if expr2: expr1 ↔ expr2
7) logical universal quantification: ∀x
8) logical existential quantification: ∃x
9) available logical variable: u,v,w,x,y,z. Try to use them.
10) nested expressions (an expression as an argument of another expression, e.g Film(Video(x))) are invalid in this FOL formulation
The invalid characters are: ∈,∉,=,≠,≤,≥,<,>,True,False
These characters will lead to errors.Because the solver can not recognize them.
And, don't output in latex.The solver can not recognize latex.
"""
        self.chat_msg = ""
        self.json_msg = """
The user will provide some thought process for translating natural language to first-order logic language. You need to get all the premise formulas and a final conclusion formula. Please parse the "premise", "conclusion" and output it in JSON format.
EXAMPLE INPUT:
Premises:
1.Text:No criminal is kind.
Predicates:
Kind(x),Criminal(x)
Fol:∀x (Criminal(x) → ¬Kind(x))
2.Text:All person who breaks the law is a criminals.
Predicates:
BreakLaw(x),Criminal(x)
Fol:∀x (BreakLaw(x) → Criminal(x))
3.Text:People are either kind or evil.
Predicates:
Kind(x),Evil(x)
Fol:∀x (Kind(x) ⊕ Evil(x))
4.Text:If someone is evil, then they are ugly.
Predicates:
Evil(x),Ugly(x)
Fol:∀x (Evil(x) → Ugly(x))
5.Text:If someone is evil, then they are cold-blood.
Predicates:
ColdBlood(x),Evil(x)
Fol:∀x (Evil(x) → ColdBlood(x))
6.Text:If Garry is either evil and ugly or neither evil nor ugly, then Garry is not evil.
Predicates:
Evil(x),Ugly(x)
Constants:
garry
Fol:((Evil(garry) ∧ Ugly(garry)) ⊕ (¬Evil(garry) ∧ ¬Ugly(garry))) → ¬Evil(garry)
Conclusion:
Text:If Garry is evil or breaks the law, then Garry is not both a criminal and breaking the law.
Predicates:
BreakLaw(x),Evil(x),Criminal(x)
Constants:
garry
Fol:(Evil(garry) ∨ BreakLaw(garry)) → ¬(Criminal(garry) ∧ BreakLaw(garry))

EXAMPLE JSON OUTPUT:
{
  "premises": [
    "∀x (Criminal(x) → ¬Kind(x))",
    "∀x (BreakLaw(x) → Criminal(x))",
    "∀x (Kind(x) ⊕ Evil(x))",
    "∀x (Evil(x) → Ugly(x))",
    "∀x (Evil(x) → ColdBlood(x))",
    "((Evil(garry) ∧ Ugly(garry)) ⊕ (¬Evil(garry) ∧ ¬Ugly(garry))) → ¬Evil(garry)"
  ],
  "conclusion": "(Evil(garry) ∨ BreakLaw(garry)) → ¬(Criminal(garry) ∧ BreakLaw(garry))"
}
"""


    def formalize(self, problem: Dict, examples: List[Dict]) -> Dict:
        """
        Input: FOLIO problem dict {premises: [...], conclusion: "..."}
        Output: {
          "premises-FOL": [...],
          "conclusion-FOL": "..."
        }
        """
        prompt = self.build_prompt(problem, examples)

        response = self.client.chat_completion([
            {"role": "system", "content": "You are a logic formalization assistant. Output JSON only."},
            {"role": "user", "content": prompt}
        ])

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"[TranslatorLLM] Invalid JSON:\n{response}")
        
    def build_prompt(self, problem: Dict, examples: List[Dict]) -> str:
        prompt = (
            "Translate the following natural language problem into First-Order Logic (FOL).\n\n"
        )
        
        # 1️⃣ Thêm luật FOL
        prompt += self.rule_msg + "\n\n"
        
        # 2️⃣ Thêm ví dụ retrieved
        if examples:
            prompt += "Here are some examples showing how a natural language sentence (premise) is translated into its corresponding First-Order Logic (FOL) formula:\n"
            for i, ex in enumerate(examples):
                prompt += f"Example {i+1}:\n"
                prompt += f"Premise: {ex['sentence']}\n"
                if ex.get("predicates"):
                    preds = ", ".join(f"{k} with {v} parameters" for k, v in ex["predicates"].items())
                    prompt += f"Parse predicates: {preds}\n"
                if ex.get("constants"):
                    consts = ", ".join(f"{k}" for k, v in ex["constants"].items())
                    prompt += f"Parse constants: {consts}\n"
                # if ex.get("variable_mapping"):
                #     vars_ = ", ".join(f"{k}->{v}" for k, v in ex["variable_mapping"].items())
                #     prompt += f"Variable mapping: {vars_}\n"
                if ex.get("translation_steps"):
                    prompt += "Translation steps:\n"
                    for step in ex["translation_steps"]:
                        prompt += f"- {step}\n"
                prompt += f"FOL: {ex['fol_formula']}\n\n"

        
        # 3️⃣ Thêm JSON guidance
        # prompt += self.json_msg + "\n\n"

        # 4️⃣ Thêm problem actual
        prompt += "Problem:\nPremises:\n"
        for p in problem["premises"]:
            prompt += f"- {p}\n"

        prompt += f"Conclusion:\n- {problem['conclusion']}\n\n"
        
        # 5️⃣ Kết thúc hướng dẫn
        prompt += (
            "Output JSON ONLY. Do NOT include any text, explanation, or comment outside JSON.\n"
            "The JSON must have exactly two fields:\n"
            "- \"premises-FOL\": list of strings representing FOL formulas\n"
            "- \"conclusion-FOL\": single string representing FOL formula\n\n"
            "EXAMPLE JSON OUTPUT:\n"
            "{\n"
            "  \"premises-FOL\": [\n"
            "    \"∀x (Criminal(x) → ¬Kind(x))\",\n"
            "    \"∀x (BreakLaw(x) → Criminal(x))\",\n"
            "    \"∀x (Kind(x) ⊕ Evil(x))\",\n"
            "    \"∀x (Evil(x) → Ugly(x))\",\n"
            "    \"∀x (Evil(x) → ColdBlood(x))\",\n"
            "    \"((Evil(garry) ∧ Ugly(garry)) ⊕ (¬Evil(garry) ∧ ¬Ugly(garry))) → ¬Evil(garry)\"\n"
            "  ],\n"
            "  \"conclusion-FOL\": \"(Evil(garry) ∨ BreakLaw(garry)) → ¬(Criminal(garry) ∧ BreakLaw(garry))\"\n"
            "}\n"
        )
        print("========= PROMPT =========")
        print(prompt)
        return prompt
