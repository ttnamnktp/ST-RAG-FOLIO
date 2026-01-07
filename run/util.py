from data.data_loader import JsonlDatasetLoader
from agent.naive_predictor.naive_predictor import NaivePredictor
from llm.llm_client import LLMClient

def run(data_file="data/folio-validation.jsonl", data_num=204, predictor=NaivePredictor):
    loader = JsonlDatasetLoader(data_file)
    dataset = loader.load()[:data_num] # load 5 data đầu

    llm = LLMClient()
    predictor = predictor(llm)

    correct = 0

    for i, sample in enumerate(dataset):
        pred = predictor.predict(sample)
        gold = sample["label"]

        print(f"[{i}] Pred: {pred:10s} | Gold: {gold}")

        if pred == gold:
            correct += 1

    acc = correct / len(dataset)
    print(f"\nAccuracy: {acc:.2%}")