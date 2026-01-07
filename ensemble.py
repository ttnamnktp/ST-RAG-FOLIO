import re
from data.data_loader import JsonlDatasetLoader

def read_predictions(txt_path):
    naive = []
    rag = []
    translate = []

    current = None  # đang đọc model nào

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # xác định block
            if line.lower().startswith("naive predictor"):
                current = "naive"
                continue
            elif line.lower().startswith("rag predictor"):
                current = "rag"
                continue
            elif line.lower().startswith("translate predictor"):
                current = "translate"
                continue

            # match dòng prediction
            m = re.search(r"Pred:\s*(True|False|Uncertain)", line)
            if not m or current is None:
                continue

            label = m.group(1)

            if current == "naive":
                naive.append(label)
            elif current == "rag":
                rag.append(label)
            elif current == "translate":
                translate.append(label)

    return naive, rag, translate

naive, rag, translate = read_predictions("predictions.txt")
# print(len(naive), len(rag), len(translate))
# print(naive[:15])
# print(rag[:15])
# print(translate[:15])

from collections import Counter

def majority_vote(preds):
    cnt = Counter(preds)
    most_common = cnt.most_common()
    
    if len(most_common) == 1:
        return most_common[0][0]
    
    # kiểm tra hòa
    if most_common[0][1] == most_common[1][1]:
        return preds[1]
    
    return most_common[0][0]


final_preds = []
for i in range(len(naive)):
    preds = [naive[i], rag[i], translate[i]]
    final_preds.append(majority_vote(preds))

loader = JsonlDatasetLoader("data/folio-validation.jsonl")
dataset = loader.load()
gold_labels = [x["label"] for x in dataset]

correct = sum(p == g for p, g in zip(final_preds, gold_labels))
accuracy = correct / len(gold_labels)

print(f"Accuracy: {accuracy:.4f}")
