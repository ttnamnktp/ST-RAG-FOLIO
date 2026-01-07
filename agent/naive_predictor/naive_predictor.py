# agent/predictors/naive_predictor.py
from typing import Dict
from agent.base_predictor import BasePredictor

class NaivePredictor(BasePredictor):

    def build_prompt(self, sample: Dict) -> list:
        premises = "\n".join(sample["premises"])
        conclusion = sample["conclusion"]

        return [
            {
                "role": "system",
                "content": (
                    "You are a logical reasoner.\n"
                    "Decide whether the conclusion is logically entailed.\n"
                    "Answer strictly with: True, False, or Uncertain."
                )
            },
            {
                "role": "user",
                "content": f"""
Premises:
{premises}

Conclusion:
{conclusion}
"""
            }
        ]

    def predict(self, sample: Dict) -> str:
        messages = self.build_prompt(sample)
        output = self.llm.chat_completion(messages)
        return self.normalize(output)
