import json, os
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_ai2"
out = []
d3 = json.load(open(os.path.join(base, "003.json"), encoding="utf-8"))
out.append("=== 003 cand c300-319 ===")
for x in d3["cand"]:
    if x["c"] >= 300:
        out.append(f'c{x["c"]}: {x["text"][:90]}')
out.append("=== 003 items z640-661 ===")
for x in d3["items"]:
    if x["z"] >= 640:
        out.append(f'z{x["z"]}: {x["text"][:90]}')
d2 = json.load(open(os.path.join(base, "002.json"), encoding="utf-8"))
out.append("=== 002 cand c260-279 ===")
for x in d2["cand"]:
    if x["c"] >= 260:
        out.append(f'c{x["c"]}: {x["text"][:90]}')
out.append("=== 002 items z450-470 ===")
for x in d2["items"][:20]:
    out.append(f'z{x["z"]}: {x["text"][:90]}')
open(os.path.join(base, "_peek4.txt"), "w", encoding="utf-8").write("\n".join(out))
print("ok")
