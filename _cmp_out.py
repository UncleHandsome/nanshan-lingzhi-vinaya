# -*- coding: utf-8 -*-
import os, sys, csv, json

base = os.path.dirname(os.path.abspath(__file__))

def load_paras(book, chunk):
    p = os.path.join(base, "AI語譯", "out", book, chunk + ".txt")
    with open(p, encoding="utf-8") as f:
        txt = f.read()
    paras = [x.strip() for x in txt.replace("\r\n", "\n").split("\n\n")]
    paras = [x for x in paras if x]
    return paras

rep = os.path.join(base, "AI語譯", "_work", "review", "report_t2.tsv")
with open(rep, encoding="utf-8") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

p0 = [r for r in rows if r["level"] == "P0"]
out = []
for i, r in enumerate(p0):
    b, c, s = r["book"], r["chunk"], r["seg"]
    cur = r.get("current") or ""
    try:
        paras = load_paras(b, c)
        n = len(paras)
        seg = int(s)
        target = paras[seg-1] if 1 <= seg <= n else "<OUT OF RANGE>"
    except Exception as e:
        target = "<ERR %s>" % e
        n = -1
    out.append("=" * 100)
    out.append("[%d] %s %s seg %s  (out paras=%d)" % (i, b, c, s, n))
    out.append("--- report current (len=%d) ---" % len(cur))
    out.append(cur)
    out.append("--- out file para[seg] (len=%d) ---" % len(target))
    out.append(target)
    out.append("--- identical? %s" % (cur.strip() == target.strip()))
    out.append("")

with open(os.path.join(base, "_p0_vs_out.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("ok")
