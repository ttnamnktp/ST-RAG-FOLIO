# agent/naive_predictors/reasoning_predictor.py
from typing import Dict
from agent.base_predictor import BasePredictor

class ReasoningPredictor(BasePredictor):

    def build_reasoning_prompt(self, sample: Dict) -> list:
        premises = "\n".join(sample["premises"])
        conclusion = sample["conclusion"]

        return [
            {
                "role": "system",
                "content": (
                    "You are a first-order logic reasoner.\n"
                    "Derive step-by-step whether the conclusion follows from the premises.\n"
                    "Use formal logical reasoning."
                )
            },
            {
                "role": "user",
                "content": f"""
Premises:
{premises}

Conclusion:
{conclusion}

Provide a detailed logical reasoning.
"""
            }
        ]
    
    def build_decision_prompt(self, reasoning: str) -> list:
        return [
            {
                "role": "system",
                "content": (
                    "Based on the reasoning, decide the final answer.\n"
                    "Answer strictly with one word: True, False, or Uncertain."
                )
            },
            {
                "role": "user",
                "content": reasoning
            }
        ]
        
    def predict(self, sample: Dict) -> str:
        # Step 1: reasoning
        reasoning_messages = self.build_reasoning_prompt(sample)
        reasoning = self.llm.chat_completion(reasoning_messages)

        # (optional) log reasoning
        # print("Reasoning:\n", reasoning)

        # Step 2: final decision
        decision_messages = self.build_decision_prompt(reasoning)
        decision = self.llm.chat_completion(decision_messages)

        return self.normalize(decision)


