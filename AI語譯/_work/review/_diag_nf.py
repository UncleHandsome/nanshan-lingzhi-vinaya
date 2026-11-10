# -*- coding: utf-8 -*-
import csv, re, json
from collections import OrderedDict

P = r"AI語譯/_work/review/report_re9.tsv"
rows = []
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10: continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        d["_line"] = i
        rows.append(d)

def find_pat(sug):
    ops = []
    pat = re.compile(r"將「([^」]*)」([^。；]{0,40}?)改為「([^」]*)」")
    for m in pat.finditer(sug):
        ops.append((m.group(1), m.group(3), "AtoB"))
    if ops: return ops
    pat2 = re.compile(r"「([^」]*)」([^。；]{0,40}?)改為「([^」]*)」")
    for m in pat2.finditer(sug):
        ops.append((m.group(1), m.group(3), "AtoB"))
    return ops

def quotes(s):
    return re.findall(r"「([^」]{2,})」", s)

out = []
for d in rows:
    sug = d["suggestion"].strip()
    if not sug: continue
    ops = find_pat(sug)
    if not ops: continue
    cur = d["current"]
    miss = [(a,b) for a,b,k in ops if a not in cur]
    if not miss: continue
    out.append("="*100)
    out.append(f"line={d['_line']} {d['chunk']} seg={d['seg']} {d['level']} {d['cls']}")
    out.append(f"SUG: {sug}")
    for a,b in miss:
        cntA = cur.count(a)
        cntB = cur.count(b)
        out.append(f"  A(len {len(a)}) count={cntA}: {a[:300]}")
        out.append(f"  B(len {len(b)}) count={cntB}: {b[:300]}")
    # print any long quotes from problem that DO occur in current
    for q in quotes(d["problem"]):
        if len(q) >= 6 and q in cur:
            out.append(f"  [problem-quote IN current ({cur.count(q)}x)] {q[:200]}")
    out.append(f"  PROBLEM: {d['problem'][:600]}")

open(r"AI語譯/_work/review/_notfound_g1.txt","w",encoding="utf-8").write("\n".join(out))
print("notfound detail lines", len(out))
