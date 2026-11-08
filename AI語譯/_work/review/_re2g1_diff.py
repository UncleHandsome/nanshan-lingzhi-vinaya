import json, io, os, difflib

BASE = r"AI語譯\_work\review"
rows = json.load(open(os.path.join(BASE, "_re2g1_rows.json"), encoding="utf-8"))
ops = json.load(open(os.path.join(BASE, "_re2g1_ops_merged.json"), encoding="utf-8"))
ops = {int(k): v for k, v in ops.items()}

lines = []
for i, r in enumerate(rows, 1):
    op = ops[i]
    if "skip" in op:
        continue
    cur = r["current"].replace("\n", " ")
    t = op.get("full")
    if t is None:
        t = cur
        for e in op["edits"]:
            t = t.replace(e[0], e[1])
    sm = difflib.SequenceMatcher(None, cur, t, autojunk=False)
    for tag, a0, a1, b0, b1 in sm.get_opcodes():
        if tag == "equal":
            continue
        pre = cur[max(0, a0 - 18):a0]
        post = cur[a1:a1 + 18]
        lines.append(f"[{i}] {r['chunk']} seg{r['seg']}\n  …{pre}【{cur[a0:a1]}】{post}…\n  →…{pre}【{t[b0:b1]}】{post}…")

with io.open(os.path.join(BASE, "_re2g1_diff.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("diff blocks:", len(lines))
