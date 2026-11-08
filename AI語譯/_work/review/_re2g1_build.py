import json, io, os, difflib

BASE = r"AI語譯\_work\review"
rows = json.load(open(os.path.join(BASE, "_re2g1_rows.json"), encoding="utf-8"))
ops = json.load(open(os.path.join(BASE, "_re2g1_ops_merged.json"), encoding="utf-8"))
ops = {int(k): v for k, v in ops.items()}

report = []
newtext = {}
for i, r in enumerate(rows, 1):
    op = ops[i]
    cur = r["current"]
    if "skip" in op:
        report.append((i, "SKIP", op["skip"]))
        continue
    t = op["full"] if "full" in op else cur
    if "edits" in op:
        for e in op["edits"]:
            old, new = e[0], e[1]
            want = e[2] if len(e) > 2 else 1
            n = t.count(old)
            assert n == want, (i, n, want, old[:40])
            t = t.replace(old, new)
    t = t.replace("\r\n", " ").replace("\n", " ").strip()
    assert "\t" not in t
    newtext[i] = t

# dedupe by (book, chunk, seg)
groups = {}
for i, r in enumerate(rows, 1):
    if i not in newtext:
        continue
    key = (r["book"], r["chunk"], r["seg"])
    groups.setdefault(key, []).append(i)

conflicts = []
out = []
for key, ids in groups.items():
    texts = {newtext[i] for i in ids}
    if len(texts) > 1:
        conflicts.append((key, ids, [len(newtext[i]) for i in ids]))
    else:
        out.append((key[0], key[1], key[2], newtext[ids[0]], ids))

print("groups:", len(groups), "conflicts:", len(conflicts))
for c in conflicts:
    print("CONFLICT", c)

# order by original row order
order = {key: min(ids) for key, ids in groups.items()}
out.sort(key=lambda x: order[(x[0], x[1], x[2])])

with io.open(os.path.join(BASE, "fix_re2_g1.tsv"), "w", encoding="utf-8", newline="\n") as f:
    for book, chunk, seg, t, ids in out:
        f.write(f"{book}\t{chunk}\t{seg}\t{t}\n")

print("wrote lines:", len(out))
skips = [i for i in range(1, len(rows) + 1) if i not in newtext]
print("processed rows:", len(newtext), "skipped rows:", len(skips))
print("skipped:", skips)

# sanity checks
bad = []
for book, chunk, seg, t, ids in out:
    if "。。" in t or "，。" in t or "、、" in t or "〕〕" in t or "））" in t or "「「" in t or "」」" in t:
        bad.append((seg, t[:60]))
print("punct anomalies:", bad)
sizes = sorted((len(t), seg) for _, _, seg, t, _ in out)
print("shortest:", sizes[:3], "longest:", sizes[-2:])
