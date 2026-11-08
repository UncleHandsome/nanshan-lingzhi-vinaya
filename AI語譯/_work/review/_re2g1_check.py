import json, glob, os

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
newtext = {}
for i in sorted(ops):
    op = ops[i]
    if "skip" in op:
        continue
    cur = rows[i - 1]["current"]
    if "full" in op:
        t = op["full"]
    else:
        t = cur
        for e in op["edits"]:
            old, new = e[0], e[1]
            want = e[2] if len(e) > 2 else 1
            n = t.count(old)
            if n != want:
                errs.append((i, f"count={n} want={want}", old[:50]))
                break
            t = t.replace(old, new)
    t = t.replace("\r\n", " ").replace("\n", " ")
    if "\t" in t:
        errs.append((i, "tab"))
    if t == cur:
        errs.append((i, "unchanged"))
    newtext[i] = t

print("ops:", len(ops), "errs:", len(errs))
for e in errs:
    print("ERR", e)
missing = [i for i in range(1, len(rows) + 1) if i not in ops]
print("rows without op:", len(missing), missing)
skips = [i for i in sorted(ops) if "skip" in ops[i]]
print("skips:", len(skips), skips)
print("new chars total:", sum(len(v) for v in newtext.values()))
