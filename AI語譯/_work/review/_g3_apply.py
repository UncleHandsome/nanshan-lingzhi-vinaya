import json, glob, sys, os
base = r"AI語譯\_work\review"
rows = json.load(open(os.path.join(base, "_g3_rows.json"), encoding="utf-8"))
ops = {}
files = sorted(glob.glob(os.path.join(base, "_g3_ops*.json")))
for fp in files:
    for op in json.load(open(fp, encoding="utf-8")):
        if op["i"] in ops:
            raise SystemExit(f"duplicate op {op['i']} in {fp}")
        ops[op["i"]] = op
print("ops files:", [os.path.basename(f) for f in files], "ops:", len(ops))
newtext = {}
errs = []
for i, op in ops.items():
    cur = rows[i]["current"]
    t = cur
    for old, new in op.get("edits", []):
        n = t.count(old)
        if n != 1:
            errs.append((i, n, old[:40]))
            continue
        t = t.replace(old, new)
    newtext[i] = t
if errs:
    print("MATCH ERRORS:")
    for e in errs:
        print(e)
missing = [i for i in range(len(rows)) if i not in ops]
print("missing ops:", missing)
same = [i for i in newtext if newtext[i] == rows[i]["current"]]
print("unchanged:", same)
bad = [i for i, t in newtext.items() if "\t" in t or "\n" in t or "\r" in t]
print("bad chars:", bad)
json.dump({str(k): v for k, v in newtext.items()}, open(os.path.join(base, "_g3_new.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
if len(ops) == len(rows) and not errs:
    outp = os.path.join(base, "fix_all_g3.tsv")
    with open(outp, "w", encoding="utf-8", newline="\n") as f:
        for i, r in enumerate(rows):
            f.write(f"{r['book']}\t{r['chunk']}\t{r['seg']}\t{newtext[i]}\n")
    print("WROTE", outp)
