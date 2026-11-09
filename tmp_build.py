# -*- coding: utf-8 -*-
import json, difflib, re, sys

data = json.load(open("AI語譯/_work/review/tmp_re8/groups.json", encoding="utf-8"))
applied = {int(k): v for k, v in json.load(open("AI語譯/_work/review/tmp_re8/applied.json", encoding="utf-8")).items()}

# occurrence audit from edits definition
import importlib.util
# read old strings by re-executing the edits dict portion: simpler to import tmp_apply? it runs and overwrites. Instead parse via exec of the file up to results loop.
src = open("tmp_apply.py", encoding="utf-8").read()
ns = {}
exec(src.split("skip_idx =")[0].replace('data = json.load(open("AI語譯/_work/review/tmp_re8/groups.json", encoding="utf-8"))', 'data=[]'), ns)
edits = ns["edits"]

multi = []
for i, ops in edits.items():
    cur = data[i][1][0]["current"]
    for old, rep in ops:
        if old == "__WHOLE__":
            continue
        c = cur.count(old)
        if c > 1:
            multi.append((i, c, old))
print("OLD strings appearing >1 time:", len(multi))
for m in multi:
    print("  MULTI", m[0], m[1], m[2][:60])

# build rows
rows = []
lines = []
for i, (k, gs) in enumerate(data):
    if i not in applied:
        continue
    new = applied[i]
    new = new.replace("\r", "").replace("\n", "")
    assert "\t" not in new, (i, "TAB")
    book, chunk, seg = k
    rows.append((book, chunk, seg, new))
    lines.append("\t".join([book, chunk, seg, new]))

with open("AI語譯/_work/review/fix_re8_g3.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("output rows:", len(rows))

# diff report
out = []
for (book, chunk, seg, new) in rows:
    i = next(idx for idx in applied if data[idx][0] == [book, chunk, seg])
    cur = data[i][1][0]["current"].replace("\n", "")
    sm = difflib.SequenceMatcher(None, cur, new, autojunk=False)
    out.append(f"===== {i} | {book} | {chunk} | seg {seg}")
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        out.append(f"  [{tag}] -{cur[max(0,i1-25):i2+25]!r}")
        out.append(f"          +{new[max(0,j1-25):j2+25]!r}")
open("AI語譯/_work/review/tmp_re8/diff.txt", "w", encoding="utf-8").write("\n".join(out))
print("diff lines:", len(out))
