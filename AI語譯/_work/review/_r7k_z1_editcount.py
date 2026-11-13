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
                out.extend(v)
            return out
    return []

edits = []
for fn in ["_r7k_z1_patch05a.py", "_r7k_z1_patch05b.py", "_r7k_z1_patch05c.py", "_r7k_z1_patch_extra.py"]:
    edits.extend(load_edits(os.path.join(REV, fn)))

segs = json.load(open(os.path.join(REV, "_r7k_z1_segs.json"), encoding="utf-8"))
def lines(p):
    return [l for l in open(p, encoding="utf-8", newline="").read().splitlines() if l.strip()]

# backup lines per chunk
chunks = ["05a_卷中之一", "05b_卷中之一", "05c_卷中之一"]
old = {c: lines(os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔", c + "_v.txt")) for c in chunks}
counts = {c: [0]*len(old[c]) for c in chunks}
missing = []
for olds, news in edits:
    found = False
    for c in chunks:
        for i, ln in enumerate(old[c]):
            if olds in ln:
                counts[c][i] += 1
                found = True
                break
        if found:
            break
    if not found:
        missing.append(olds[:30])
print("edits", len(edits), "unmapped", len(missing))
for m in missing: print("MISS", m)

# map segment idx -> edits
per_file = {}
for s in segs:
    f = s["file"]; c = s["chunk"]; i = s["idx"]
    if c not in old:
        continue
    per_file[f] = per_file.get(f, 0) + counts[c][i-1]
for f in ["128","129","130","131","132","133","134","135","136","137","138","139","140",
          "141","142","143","144","145","146","147","148","149","150","151","152","153","154","155","156",
          "158","159","160","161","162","163","164","165","166","167","168","169","170","171","2809"]:
    print(f, per_file.get(f, 0))
print("TOTAL", sum(per_file.values()))
