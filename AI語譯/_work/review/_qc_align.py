# -*- coding: utf-8 -*-
import json, re

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯"
recs = json.load(open(BASE + r"\_work\review\_qc_rows.json", encoding="utf-8"))

def load(chunk):
    p = BASE + r"\out\資持記\%s.txt" % chunk
    try:
        lines = [l.rstrip("\n") for l in open(p, encoding="utf-8")]
    except FileNotFoundError:
        return None
    paras = [l for l in lines if l.strip()]
    return paras

out = []
for gid in ["06-0046", "06-0048", "06-0067", "06-0068"]:
    d = [r for r in recs if r["gid"] == gid][0]
    paras = load(d["chunk"])
    out.append("== %s %s seg %s nparas %d" % (gid, d["chunk"], d["seg"], len(paras)))
    head = d["current"][:25]
    hits = [i + 1 for i, p in enumerate(paras) if p.startswith(head[:15])]
    out.append("   report current head: %s -> ordinal %s" % (head, hits))
    head2 = d["tr"][:20]
    hits2 = [i + 1 for i, p in enumerate(paras) if p.startswith(head2[:12])]
    out.append("   tr head: %s -> ordinal %s" % (head2, hits2))
open(BASE + r"\_work\review\_qc_align.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
