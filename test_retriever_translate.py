# from  agent.ltrag.retrieval.retriever_translate import TranslationRetriever
# if __name__ == "__main__":
#     retriever = TranslationRetriever("data/translation-kb.json")
#     query = "Where is North Yorkshire?"
#     results = retriever.retrieve(query)
#     for r in results:
#         print("Sentence:", r["sentence"])
#         print("FOL:", r["fol_formula"])
#         print("Steps:", r["translation_steps"])
#         print("----")

from  agent.ltrag.retrieval.story_retriever import StoryRetriever
if __name__ == "__main__":
    retriever = StoryRetriever("data/translation-kb.json")
    query = "Where is North Yorkshire?"
    results = retriever.retrieve(query)
    for r in results:
        print(r)

# FOLIO/fix_json_kb.py
# import json

# input_file = "data/translation-kb.jsonl"  # file cũ
# output_file = "data/translation-kb-fixed.json"  # file mới

# objects = []
# with open(input_file, "r", encoding="utf-8") as f:
#     current_obj_lines = []
#     for line in f:
#         line = line.strip()
#         if not line:
#             continue  # bỏ dòng trống
#         if line.startswith("{") and current_obj_lines:
#             # kết thúc object cũ
#             obj_text = "\n".join(current_obj_lines)
#             obj = json.loads(obj_text)  # parse JSON object
#             objects.append(obj)
#             current_obj_lines = [line]  # bắt đầu object mới
#         else:
#             current_obj_lines.append(line)
#     # add object cuối cùng
#     if current_obj_lines:
#         obj_text = "\n".join(current_obj_lines)
#         obj = json.loads(obj_text)
#         objects.append(obj)

# # ghi ra JSON array multi-line
# with open(output_file, "w", encoding="utf-8") as f:
#     json.dump(objects, f, indent=2)

# print(f"Fixed JSON KB saved to {output_file}, {len(objects)} entries")
