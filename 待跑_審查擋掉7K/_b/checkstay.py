# -*- coding: utf-8 -*-
"""確認 51 段改動仍在現行檔中（防併行寫入覆蓋）。"""
import io, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit2

HERE = os.path.dirname(os.path.abspath(__file__))
e = json.loads(io.open(os.path.join(HERE, "edits_all.json"), encoding="utf-8").read())
order = ["695", "698", "699", "700", "701", "804", "841", "1098", "1112", "1207", "1250", "1256"]
bad = 0
for nnn in order:
    segs = {s["no"]: s for s in kit2.parse7k(nnn)}
    for no, pairs in e[nnn].items():
        s = segs[no]
        cur = kit2.cur_text(s)
        for p in pairs:
            if p["new"] not in cur:
                bad += 1
                print("MISSING %s %s#%d : %r" % (no, s["chunk"], s["idx"], p["new"][:40]))
print("total missing:", bad)
