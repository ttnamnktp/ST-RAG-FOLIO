accuracy = 0
count = 0
ignored = 0

# with open("translateqwen14.txt", "r", encoding="utf-8") as f:
with open("translate_none.txt", "r", encoding="utf-8") as f:

    lines = f.readlines()

skip_next = False
for line in lines:
    line = line.strip()
    if not line:
        continue
    
    # Nếu dòng bắt đầu bằng "Error:", đánh dấu skip
    if line.startswith("Error:"):
    # if line.startswith("=== Parsing successfully ==="):
        skip_next = True
        ignored += 1
        continue
    
    # Kiểm tra dòng chứa Pred | Gold
    if "Pred:" in line and "Gold:" in line:
        if skip_next:
            # sample này bị lỗi, bỏ qua
            skip_next = False
            continue
        # Lấy giá trị Pred và Gold
        try:
            pred_part = line.split("Pred:")[1].split("|")[0].strip()
            gold_part = line.split("Gold:")[1].strip()
        except IndexError:
            # Nếu format sai, bỏ qua
            continue
        
        if pred_part == gold_part:
            accuracy += 1
        count += 1
        # skip_next = True

print(f"Accuracy: {accuracy}/{count} = {accuracy/count:.4f}")
print(f"Ignored samples due to errors: {ignored}")
# print(f"Not ignored samples due to errors: {ignored}")

