# -*- coding: utf-8 -*-
import csv, re
P = r"AI語譯/_work/review/report_re9.tsv"
rows = {}
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10: continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        d["_line"] = i
        rows[i] = d

d = rows[152]
cur = d["current"]
for m in re.finditer("自誓得戒", cur):
    s = max(0, m.start()-60); print("[152]", cur[s:m.start()+180].replace("\n","\n    "))
    print("..")

print("="*80)
d = rows[157]
cur = d["current"]
for probe in ["偷形", "不受法事", "《僧祇》", "可以嗎"]:
    print(probe, cur.count(probe))
idx = cur.find("偷形")
print(repr(cur[max(0,idx-100):idx+250]))
