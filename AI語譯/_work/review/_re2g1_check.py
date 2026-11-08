import json, glob, os, sys

BASE = r"AI語譯\_work\review"
rows = json.load(open(os.path.join(BASE, "_re2g1_rows.json"), encoding="utf-8"))

ops = {}
for fp in sorted(glob.glob(os.path.join(BASE, "_re2g1_ops_*.jsonl"))):
    for ln in open(fp, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        op = json.loads(ln)
        if op["i"] in ops:
            raise SystemExit(f"dup op {op['i']} in {fp}")
        ops[op["i"]] = op

errs = []
for i in sorted(ops):
    op = ops[i]
    if "skip" in op:
        continue
    cur = rows[i - 1]["current"]
    if "full" in op:
        t = op["full"]
        if "\t" in t or "\n" in t:
            errs.append((i, "bad chars in full"))
        continue
    t = cur
    for old, new in op["edits"]:
        n = t.count(old)
        if n != 1:
            errs.append((i, n, old[:50]))
            break
        t = t.replace(old, new)
    if "\t" in t or "\n" in t:
        errs.append((i, "bad chars"))

print("ops:", len(ops), "errs:", len(errs))
for e in errs:
    print("ERR", e)
missing = [i for i in range(1, len(rows) + 1) if i not in ops]
print("rows without op:", len(missing))
print(missing)
skips = [i for i in sorted(ops) if "skip" in ops[i]]
print("skips:", len(skips), skips)
