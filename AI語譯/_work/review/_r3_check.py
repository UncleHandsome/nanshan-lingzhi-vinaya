# -*- coding: utf-8 -*-
"""ret3 套用：套用前檢查（命次數、段數、行尾）＋前後預覽；不寫檔。"""
import io
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r3_lib as L

dat = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r3_edits.json"), encoding="utf-8"))

print("== 逐條命中檢查 ==")
byfile = {}
for e in dat:
    byfile.setdefault((e["book"], e["chunk"]), []).append(e)
for (book, chunk), es in byfile.items():
    t, s, ps = L.parts(book, chunk)
    print("[%s %s] 段數=%d 行數=%d CR=%d" % (book, chunk, len(ps), t.count("\n"), t.count("\r")))
    for e in es:
        p = ps[e["para"] - 1]
        c = p.count(e["old"])
        tot = t.count(e["old"])
        flag = "OK" if c == 1 else "!!"
        print("  %-2s #%-3d 段內=%d 全檔=%d %s | %s" % (flag, e["para"], c, tot, e["item"], e["old"][:28]))

print()
print("== 前後對照 ==")
for e in dat:
    p = L.para(e["book"], e["chunk"], e["para"])
    i = p.find(e["old"])
    print("--- [%d] %s  (%s#%d) ---" % (e["no"], e["item"], e["chunk"], e["para"]))
    print("前：…" + p[max(0, i - 40):i + len(e["old"]) + 40] + "…")
    q = p.replace(e["old"], e["new"])
    j = q.find(e["new"])
    print("後：…" + q[max(0, j - 40):j + len(e["new"]) + 40] + "…")
    print()
