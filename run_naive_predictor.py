# run_folio_validation.py
from data.data_loader import JsonlDatasetLoader
from agent.naive_predictor.naive_predictor import NaivePredictor
from llm.llm_client import LLMClient
from run.util import run

def main():
    loader = JsonlDatasetLoader("data/folio-validation.jsonl")
    dataset = loader.load()[:200] 

    llm = LLMClient()
    predictor = NaivePredictor(llm)

    correct = 0

    for i, sample in enumerate(dataset):
        pred = predictor.predict(sample)
        gold = sample["label"]

        print(f"[{i}] Pred: {pred:10s} | Gold: {gold}")

        if pred == gold:
            correct += 1

    acc = correct / len(dataset)
    print(f"\nAccuracy: {acc:.2%}")

if __name__ == "__main__":
    run()
