# -*- coding: utf-8 -*-
"""依 _7k01_plans/fNNN.json 套用某檔修訂。用法: python _7k01_run.py 9"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _7k01_lib as L

plan_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_7k01_plans")
n = int(sys.argv[1])
p = os.path.join(plan_dir, "f%03d.json" % n)
entries = json.load(open(p, encoding="utf-8"))
for e in entries:
    rec = L.apply(e["chunk"], e["seg"], [tuple(x) for x in e["edits"]], e.get("note", ""))
    print("OK %s %s#%d  %d edits" % (e.get("id", "?"), e["chunk"], e["seg"], len(rec["edits"])))
    for d in rec["diff"]:
        print("    - %s\n    + %s" % (d["old"], d["new"]))
