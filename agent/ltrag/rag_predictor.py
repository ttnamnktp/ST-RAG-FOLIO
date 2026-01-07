# agent/ltrag/retrieval_predictor.py
from typing import Dict, List
from agent.base_predictor import BasePredictor
from agent.ltrag.retrieval.retriever import Retriever

class RetrievalPredictor(BasePredictor):
    def __init__(self, llm, kb_path: str = "data", top_k: int = 5):
        super().__init__(llm)
        self.retriever = Retriever(kb_path)
        self.top_k = top_k

    def build_query_text(self, sample: Dict) -> str:
        """
        Tạo query để retrieve từ KB
        """
        premises = " ".join(sample["premises"])
        conclusion = sample["conclusion"]
        return f"{premises} Therefore {conclusion}"

    def format_examples(self, examples: List[Dict]) -> str:
        """
        Format examples để đưa vào prompt
        Giả sử mỗi example có:
          - premises
          - conclusion
          - label
        """
        formatted = []
        for ex in examples:
            formatted.append(
                f"""Premises:
{chr(10).join(ex["premises"])}

Conclusion:
{ex["conclusion"]}

Answer: {ex["label"]}
"""
            )
        return "\n---\n".join(formatted)

    def build_prompt(self, sample: Dict, examples: List[Dict]) -> list:
        examples_text = self.format_examples(examples)

        premises = "\n".join(sample["premises"])
        conclusion = sample["conclusion"]

        return [
            {
                "role": "system",
                "content": (
                    "You are a first-order logic entailment classifier.\n"
                    "Use the given examples to decide whether the conclusion\n"
                    "follows from the premises.\n"
                    "Answer strictly with one word: True, False, or Uncertain."
                )
            },
            {
                "role": "user",
                "content": f"""
Here are some examples:

{examples_text}

===
Now solve the following problem:

Premises:
{premises}

Conclusion:
{conclusion}

Answer:
"""
            }
        ]

    def predict(self, sample: Dict) -> str:
        # Step 1: build retrieval query
        query = self.build_query_text(sample)

        # Step 2: retrieve top-k examples
        examples = self.retriever.retrieve(query, top_k=self.top_k)

        # Step 3: build prompt with retrieved examples
        messages = self.build_prompt(sample, examples)
        print("======== PROMPT ========")
        print(messages)

        # Step 4: LLM decision
        decision = self.llm.chat_completion(messages)

        return self.normalize(decision)
