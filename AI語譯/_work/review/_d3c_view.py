# -*- coding: utf-8 -*-
"""Build 下三_c view files with resp + source + current, alignment-aware."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _d3c_lib as L


def build(n):
    os.makedirs(L.VIEW, exist_ok=True)
    rp = os.path.join(L.RESP, "resp_%d.txt" % n)
    items = L.mat_map(n)
    bychunk = {}
    for it in items:
        bychunk.setdefault(it["chunk"], []).append(it)
    cache = {}
    located = []
    for c, its in bychunk.items():
        loc, cache = L.locate(its, c, cache)
        located.extend(loc)
    buf = ["#" * 8 + " 意見 resp_%d " % n + "#" * 8]
    buf.append(L.read(rp).strip() if os.path.exists(rp) else "(缺意見)")
    buf.append("")
    buf.append("#" * 8 + " 段落 %d（%d 段）" % (n, len(items)) + "#" * 8)
    for it, no, note in located:
        lines = cache[it["chunk"]]
        ne = [l.strip() for l in lines if l.strip()]
        tag = "%s  mat#%d -> OUT#%s %s" % (it["seg"], it["idx"], no if no else "?", note)
        buf.append("\n--- " + tag)
        buf.append("[原文] " + it["src"])
        if no and no - 1 < len(ne):
            buf.append("[現行] " + ne[no - 1])
            if note.endswith("span") and no < len(ne):
                buf.append("[續段 OUT#%d] " % (no + 1) + ne[no])
        else:
            buf.append("[現行] <找不到對應段>")
        if it["tr"] != (ne[no - 1] if no and no - 1 < len(ne) else None):
            buf.append("[材料] " + it["tr"])
    p = os.path.join(L.VIEW, "v_%d.txt" % n)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print(p)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        build(int(a))
