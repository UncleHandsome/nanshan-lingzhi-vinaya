# -*- coding: utf-8 -*-
"""列出校閱切片的完成狀態與下一批待辦。用法：python _batch_status.py [N]"""
import os, sys, json, re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "校閱批次")
IDX = os.path.join(SRC, "_切片", "index.json")
PARTS = os.path.join(SRC, "校閱結果", "parts")

d = json.load(open(IDX, encoding="utf-8"))
todo, done = [], []
for x in d:
    for p in x["parts"]:
        rp = os.path.join(PARTS, p["report"])
        ok = False
        if os.path.exists(rp):
            t = open(rp, encoding="utf-8", errors="replace").read()
            ok = bool(re.search(r"已檢查\s*\d+\s*段", t))
        (done if ok else todo).append((p["name"], p["segs"], p["first"], p["last"]))

n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
print("已完成 %d / %d 片；待辦 %d 片" % (len(done), len(done) + len(todo), len(todo)))
print("--- 下一批 %d ---" % min(n, len(todo)))
for name, segs, a, b in todo[:n]:
    print("%s\t%d\t%s\t%s" % (name, segs, a, b))
