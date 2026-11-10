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

# check newline rows
print("--- rows whose current contains newline ---")
for i, d in rows.items():
    if "\n" in d["current"]:
        seg = d["current"]
        print(i, d["chunk"], d["seg"], "len", len(seg), "newlines at", [m.start() for m in re.finditer("\n", seg)][:10])

print()
print("--- probe line 152 ---")
d = rows[152]
cur = d["current"]
for probe in ["自誓得戒", "唯迦葉是", "這並非在阿羅漢心中得", "唯從勝緣以彰名也"]:
    print(probe, cur.count(probe))
idx = cur.find("自誓得戒")
print("context:", cur[max(0,idx-80):idx+200])
