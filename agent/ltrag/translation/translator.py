# agent/ltrag/translation/translator.py
from llm.llm_client import LLMClient
from typing import List, Dict
import json


class TranslatorLLM:
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
#         self.json_msg = """
# The user will provide some thought process for translating natural language to first-order logic language. You need to get all the premise formulas and a final conclusion formula. Please parse the "premise", "conclusion" and output it in JSON format.
# EXAMPLE INPUT:
# Premises:
# 1.Text:No criminal is kind.
# Predicates:
# Kind(x),Criminal(x)
# Fol:∀x (Criminal(x) → ¬Kind(x))
# 2.Text:All person who breaks the law is a criminals.
# Predicates:
# BreakLaw(x),Criminal(x)
# Fol:∀x (BreakLaw(x) → Criminal(x))
# 3.Text:People are either kind or evil.
# Predicates:
# Kind(x),Evil(x)
# Fol:∀x (Kind(x) ⊕ Evil(x))
# 4.Text:If someone is evil, then they are ugly.
# Predicates:
# Evil(x),Ugly(x)
# Fol:∀x (Evil(x) → Ugly(x))
# 5.Text:If someone is evil, then they are cold-blood.
# Predicates:
# ColdBlood(x),Evil(x)
# Fol:∀x (Evil(x) → ColdBlood(x))
# 6.Text:If Garry is either evil and ugly or neither evil nor ugly, then Garry is not evil.
# Predicates:
# Evil(x),Ugly(x)
# Constants:
# garry
# Fol:((Evil(garry) ∧ Ugly(garry)) ⊕ (¬Evil(garry) ∧ ¬Ugly(garry))) → ¬Evil(garry)
# Conclusion:
# Text:If Garry is evil or breaks the law, then Garry is not both a criminal and breaking the law.
# Predicates:
# BreakLaw(x),Evil(x),Criminal(x)
# Constants:
# garry
# Fol:(Evil(garry) ∨ BreakLaw(garry)) → ¬(Criminal(garry) ∧ BreakLaw(garry))

# EXAMPLE JSON OUTPUT:
# {
#   "premises": [
#     "∀x (Criminal(x) → ¬Kind(x))",
#     "∀x (BreakLaw(x) → Criminal(x))",
#     "∀x (Kind(x) ⊕ Evil(x))",
#     "∀x (Evil(x) → Ugly(x))",
#     "∀x (Evil(x) → ColdBlood(x))",
#     "((Evil(garry) ∧ Ugly(garry)) ⊕ (¬Evil(garry) ∧ ¬Ugly(garry))) → ¬Evil(garry)"
#   ],
#   "conclusion": "(Evil(garry) ∨ BreakLaw(garry)) → ¬(Criminal(garry) ∧ BreakLaw(garry))"
# }
# """
        self.json_msg = """
    The user will provide some thought process for translating natural language to first-order logic language. You need to get all the premise formulas and a final conclusion formula. Please parse the "premise", "conclusion" and output it in JSON format.
    
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
            "Translate the following natural language problem into First-Order Logic (FOL).\n"
        )
        
        prompt += self.rule_msg

        # ===== Example =====
        # if examples:
        #     ex = examples[0]
        #     prompt += "Example:\n"

        #     for nl, fol in zip(ex["premises"], ex["premises-FOL"]):
        #         prompt += f"- Premise: {nl}\n"
        #         prompt += f"  Premise-FOL: {fol}\n"

        #     if "conclusion-FOL" in ex:
        #         prompt += f"Conclusion-FOL: {ex['conclusion-FOL']}\n"

        #     prompt += "\n"
        
        prompt += self.json_msg

        # ===== Actual problem =====
        prompt += "Problem:\nPremises:\n"
        for p in problem["premises"]:
            prompt += f"- {p}\n"

        prompt += f"Conclusion:\n- {problem['conclusion']}\n\n"

        # ===== Output format =====
        # prompt += (
        #     "Output JSON ONLY. Do NOT include any text, explanation, or comment outside JSON.\n"
        #     "The JSON must have exactly two fields:\n"
        #     "- \"premises-FOL\": list of strings representing FOL formulas\n"
        #     "- \"conclusion-FOL\": single string representing FOL formula\n"
        #     "Example:\n"
        # )

        # # JSON example built from the SAME example
        # if examples:
        #     prompt += "{\n"
        #     prompt += '  "premises-FOL": [\n'
        #     for i, fol in enumerate(ex["premises-FOL"]):
        #         comma = "," if i < len(ex["premises-FOL"]) - 1 else ""
        #         prompt += f'    "{fol}"{comma}\n'
        #     prompt += "  ],\n"
        #     prompt += f'  "conclusion-FOL": "{ex.get("conclusion-FOL", "")}"\n'
        #     prompt += "}\n"
        
        prompt += (
            "Output JSON ONLY. Do NOT include any text, explanation, or comment outside JSON.\n"
            "The JSON must have exactly two fields:\n"
            "- \"premises-FOL\": list of strings representing FOL formulas\n"
            "- \"conclusion-FOL\": single string representing FOL formula\n"
            # "Example:\n"
            # "{\n"
            # '  "premises-FOL": [\n'
            # '    "∀x (PerformTalentShow(x) → AttendEngagedSchool(x))",\n'
            # '    "∀x (PerformTalentShow(x) ∨ InactiveDisinterested(x))",\n'
            # '    "∀x (ChaperoneDance(x) → ¬Student(x))",\n'
            # '    "∀x (InactiveDisinterested(x) → ChaperoneDance(x))",\n'
            # '    "∀x (WantsAcademicCareer(x) → Student(x))"\n'
            # '  ],\n'
            # '  "conclusion-FOL": "PerformTalentShow(bonnie)"\n'
            # "}\n"
        )

        # Optional: print for debug
        # print("======== PROMPT ========")
        # print(prompt)
        # print("======== PROMPT ========")
        return prompt


    # def build_prompt(self, problem: Dict, examples: List[Dict]) -> str:
    #     prompt = (
    #         "Translate the following natural language problem into First-Order Logic (FOL).\n"
    #         "Return JSON with exactly two fields:\n"
    #         "- premises-FOL: list of FOL formulas\n"
    #         "- conclusion-FOL: single FOL formula\n\n"
    #         "Rules:\n"
    #         "- Use simple unary predicates consistently (e.g., Attend(x), PerformTalentShow(x)).\n"
    #         "- Use constants for proper names in lowercase (e.g., bonnie, sam).\n"
    #         "- Do NOT invent function symbols.\n"
    #         "- Translate sentences of the form 'either A or B, or neither A nor B' explicitly using ∧, ∨, ¬.\n"
    #         "- Keep predicates consistent across all premises and conclusion.\n\n"
    #     )

    #     # Add one example only to avoid repetition
    #     if examples:
    #         prompt += "Example:\n"
    #         ex = examples[0]
    #         prompt += f"Premises: {ex['premises']}\n"
    #         prompt += f"Premises-FOL: {ex['premises-FOL']}\n"
    #         prompt += f"Conclusion-FOL: {ex.get('conclusion-FOL', '')}\n\n"

    #     # Add the actual problem
    #     prompt += "Problem:\nPremises:\n"
    #     for p in problem["premises"]:
    #         prompt += f"- {p}\n"

    #     prompt += f"Conclusion:\n- {problem['conclusion']}\n\n"

    #     # Add output format instruction
    #     prompt += (
    #         "Output JSON ONLY. Do NOT include any text, explanation, or comment outside JSON.\n"
    #         "The JSON must have exactly two fields:\n"
    #         "- \"premises-FOL\": list of strings representing FOL formulas\n"
    #         "- \"conclusion-FOL\": single string representing FOL formula\n"
    #         "Example:\n"
    #         "{\n"
    #         '  "premises-FOL": [\n'
    #         '    "∀x (PerformTalentShow(x) → AttendEngagedSchool(x))",\n'
    #         '    "∀x (PerformTalentShow(x) ∨ InactiveDisinterested(x))",\n'
    #         '    "∀x (ChaperoneDance(x) → ¬Student(x))",\n'
    #         '    "∀x (InactiveDisinterested(x) → ChaperoneDance(x))",\n'
    #         '    "∀x (WantsAcademicCareer(x) → Student(x))"\n'
    #         '  ],\n'
    #         '  "conclusion-FOL": "PerformTalentShow(bonnie)"\n'
    #         "}\n"
    #     )

    #     # Optional: print for debug
    #     # print("======== PROMPT ========")
    #     # print(prompt)
    #     # print("======== PROMPT ========")

    #     return prompt
