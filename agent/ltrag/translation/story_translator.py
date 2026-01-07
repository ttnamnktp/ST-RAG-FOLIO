# agent/ltrag/translation/story_translator.py
from llm.llm_client import LLMClient
from typing import List, Dict
import json


class StoryTranslatorRagLLM:
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
10) nested expressions (an expression as an argument of another expression) are invalid
The invalid characters are: ∈,∉,=,≠,≤,≥,<,>,True,False
Do not output LaTeX.
"""

    def formalize(self, problem: Dict, retrieved_stories: List[Dict]) -> Dict:
        prompt = self.build_prompt(problem, retrieved_stories)

        response = self.client.chat_completion([
            {"role": "system", "content": "You are a logic formalization assistant. Output JSON only."},
            {"role": "user", "content": prompt}
        ])

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"[StoryTranslatorRagLLM] Invalid JSON:\n{response}")

    def build_prompt(self, problem: Dict, retrieved_stories: List[Dict]) -> str:
        prompt = (
            "Translate the following natural language problem into First-Order Logic (FOL).\n\n"
        )

        # 1️⃣ FOL rules
        prompt += self.rule_msg + "\n\n"

        # 2️⃣ STORY-LEVEL examples
        if retrieved_stories:
            prompt += (
                "Here are some examples showing how a natural language sentence (premise) is translated into its corresponding First-Order Logic (FOL) formula:\n"
            )

            for i, story in enumerate(retrieved_stories):
                prompt += f"Example {i+1}:\n"

                for j, entry in enumerate(story["entries"]):
                    prompt += f"Premise {j+1}: {entry['sentence']}\n"

                    # if entry.get("predicates"):
                    #     preds = ", ".join(f"{k} with {v} parameters" for k, v in entry["predicates"].items())
                    #     prompt += f"Parse predicates: {preds}\n"
                    if entry.get("predicates"):
                        preds = []
                        for pred, arity in entry["predicates"].items():
                            if arity == 1:
                                preds.append(f"{pred}(x)")
                            elif arity == 2:
                                preds.append(f"{pred}(x, y)")
                            elif arity == 3:
                                preds.append(f"{pred}(x, y, z)")
                            else:
                                vars_ = ", ".join(chr(ord('x') + i) for i in range(arity))
                                preds.append(f"{pred}({vars_})")

                        prompt += "Parse predicates:\n"
                        for p in preds:
                            prompt += f"- {p}\n"

                    if entry.get("constants"):
                        consts = ", ".join(f"{k}" for k, v in entry["constants"].items())
                        prompt += f"Parse constants: {consts}\n"

                    if entry.get("translation_steps"):
                        prompt += "Translation steps:\n"
                        for step in entry["translation_steps"]:
                            prompt += f"- {step}\n"

                    prompt += f"FOL: {entry['fol_formula']}\n\n"

                # prompt += "---- End of Example Story ----\n\n"

        # 3️⃣ Actual problem
        prompt += "Now translate the following PROBLEM:\n\n"
        prompt += "Premises:\n"
        for p in problem["premises"]:
            prompt += f"- {p}\n"

        prompt += "\nConclusion:\n"
        prompt += f"- {problem['conclusion']}\n\n"

        # 4️⃣ Output format constraints
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
        # print("========= PROMPT =========")
        # print(prompt)
        return prompt