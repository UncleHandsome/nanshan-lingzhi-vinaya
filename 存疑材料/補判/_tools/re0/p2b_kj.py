# -*- coding: utf-8 -*-
"""Build 校閱 index (10K first, then 20K/40K/80K) for all needed numbers."""
import os, re, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

data = json.load(open(os.path.join(TOOLS, "parsed.json"), encoding="utf-8"))
nums = set()
for e in data["entries"]:
    if e["verdict"] != "材料不足":
        continue
    for m in re.finditer(r"(\d{3,4})(?:-\d{4}|-#\d{1,2})?", re.sub(r"[【】]", "", e["key"])):
        nums.add(m.group(1))
print("nums", len(nums))

DIRS = ["校閱_10K", "校閱_20K", "校閱_40K", "校閱_80K"]
idx, bylabel, bynum = {}, {}, {}

def parse_file(p):
    t = rd(p)
    parts = re.split(r"^【(\d{3,4}-\d{4})】(.*)$", t, flags=re.M)
    out = []
    for i in range(1, len(parts) - 1, 3):
        code, label = parts[i], parts[i + 1].strip()
        body = parts[i + 2]
        m2 = re.search(r"【譯文】(.*)", body, re.S)
        tr = m2.group(1).strip() if m2 else ""
        src = body[:m2.start()].strip() if m2 else body.strip()
        out.append({"code": code, "label": label, "src": src.strip(), "tr": tr})
    return out

for d in DIRS:
    base = os.path.join(ROOT, d)
    if not os.path.isdir(base):
        continue
    for n in sorted(nums):
        p = os.path.join(base, f"校閱_{n}.txt")
        if not os.path.exists(p):
            continue
        for it in parse_file(p):
            idx.setdefault(it["code"], it)           # first wins (10K priority)
            bynum.setdefault(n, []).append(it)
            m = re.search(r"/([0-9]{2}[a-f]|00_卷首)[^#]*#(\d+)", it["label"])
            if m:
                bylabel.setdefault((it["label"].split("/")[0], m.group(1), int(m.group(2))), it)

print("codes", len(idx), "labels", len(bylabel), "bynum", len(bynum))
json.dump({"idx": idx,
           "bylabel": {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in bylabel.items()},
           "bynum": bynum},
          open(os.path.join(TOOLS, "kj2.json"), "w", encoding="utf-8"), ensure_ascii=False)
