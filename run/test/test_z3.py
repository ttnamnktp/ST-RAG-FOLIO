from z3_module.reasoner import check_entailment
from data.data_loader import JsonlDatasetLoader

# if __name__ == "__main__":

#     loader = JsonlDatasetLoader("data/folio-validation.jsonl")
#     dataset = loader.load()[:204]

#     total = len(dataset)
#     correct = 0          # số dự đoán đúng (kể cả miss hay không)
#     miss_count = 0       # số miss
#     evaluated = 0        # số mẫu KHÔNG miss

#     for i, sample in enumerate(dataset):
#         try:
#             pred = check_entailment(
#                 sample["premises-FOL"],
#                 sample["conclusion-FOL"]
#             )
#         except Exception as e:
#             pred = "miss"
#             print(e)
#             # print(sample["premises-FOL"])
#             # print(sample["conclusion-FOL"])
            
#         # pred = check_entailment(
#         #         sample["premises-FOL"],
#         #         sample["conclusion-FOL"]
#         #     )

#         gold = sample["label"]

#         if pred == "miss":
#             miss_count += 1
#         else:
#             evaluated += 1
#             if pred == gold:
#                 correct += 1
#             else:
#                 print(sample["premises-FOL"])
#                 print(sample["conclusion-FOL"])
#                 print(f"Label: {gold}")
#                 print(f"Pred: {pred}")

#         # print(f"[{i:03d}] Pred: {pred:10s} | Gold: {gold}")

#     # ====== METRICS ======
#     accuracy_overall = correct / total
#     accuracy_without_miss = correct / evaluated if evaluated > 0 else 0.0

#     print("\n========== SUMMARY ==========")
#     print(f"Total samples        : {total}")
#     print(f"Miss count           : {miss_count}")
#     print(f"Correct (non-miss)   : {correct}")
#     print(f"Accuracy (overall)   : {accuracy_overall:.4f}")
#     print(f"Accuracy (no miss)   : {accuracy_without_miss:.4f}")
    
sample = {'premises-FOL': ['∀u (University(u) ∧ IvyLeague(u) → Private(u))', 'MovedToNewHaven(YaleUniversity, 1716)', 'EndowmentValuedAtYaleUniversity(42.3, billionDollars)', 'OrganizedIntoCollegesAndSchools(YaleUniversity, 27)', 'ResidentialColleges(YaleUniversity, [BenjaminFranklinCollege, BerkeleyCollege, BranfordCollege, DavenportCollege, EzraStilesCollege, GraceHopperCollege, JonathanEdwardsCollege, MorseCollege, PauliMurrayCollege, PiersonCollege, SaybrookCollege, SillimanCollege, TimothyDwightCollege, TrumbullCollege])'], 'conclusion-FOL': 'MovedToNewHaven(YaleUniversity)'}

print(check_entailment(sample['premises-FOL'], sample['conclusion-FOL']))