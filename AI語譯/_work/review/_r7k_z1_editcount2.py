# -*- coding: utf-8 -*-
import os, ast, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
REV = os.path.join(ROOT, "AI語譯", "_work", "review")

def load_edits(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "EDITS" for t in node.targets):
            return ast.literal_eval(node.value)
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "PATCHES" for t in node.targets):
            d = ast.literal_eval(node.value)
            out = []
            for k, v in d.items():
                out.extend([(k, o, n) for o, n in v])
            return out
    return []

jobs = [
    ("05a_卷中之一", "_r7k_z1_patch05a.py"),
    ("05b_卷中之一", "_r7k_z1_patch05b.py"),
    ("05c_卷中之一", "_r7k_z1_patch05c.py"),
]
segs = json.load(open(os.path.join(REV, "_r7k_z1_segs.json"), encoding="utf-8"))
def lines(p):
    return [l for l in open(p, encoding="utf-8", newline="").read().splitlines() if l.strip()]
old = {c: lines(os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔", c + "_v.txt")) for c in ["05a_卷中之一","05b_卷中之一","05c_卷中之一"]}
counts = {c: [0]*len(old[c]) for c in old}
missing = []

for chunk, fn in jobs:
    for o, n in load_edits(os.path.join(REV, fn)):
        hit = False
        for i, ln in enumerate(old[chunk]):
            if o in ln:
                counts[chunk][i] += 1
                hit = True
                break
        if not hit:
            missing.append((chunk, o[:25]))

# extra patch: attribute by chunk key
for chunk, o, n in load_edits(os.path.join(REV, "_r7k_z1_patch_extra.py")):
    hit = False
    for i, ln in enumerate(old[chunk]):
        if o in ln:
            counts[chunk][i] += 1
            hit = True
            break
    if not hit:
        missing.append((chunk, o[:25]))

per_file = {}
for s in segs:
    f = s["file"]; c = s["chunk"]; i = s["idx"]
    if c in old:
        per_file[f] = per_file.get(f, 0) + counts[c][i-1]
for f in ["128","129","130","131","132","133","134","135","136","137","138","139","140",
          "141","142","143","144","145","146","147","148","149","150","151","152","153","154","155","156",
          "158","159","160","161","162","163","164","165","166","167","168","169","170","171","2809"]:
    print(f, per_file.get(f, 0))
print("TOTAL", sum(per_file.values()), "MISSING", len(missing))
for m in missing: print("MISS", m)
