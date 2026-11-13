# -*- coding: utf-8 -*-
"""7K 中四上 b：由 _z7_log.jsonl 產生登記檔（只取 1811 起）。"""
import io, json, os
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
rows = [json.loads(l) for l in io.open("_z7_log.jsonl", encoding="utf-8") if l.strip()]
rows = [r for r in rows if r["n"] >= 1811]
out = [u"檔號\t卷\t改段數\t義理修正\t潤飾\t否決\t存疑\t備註"]
for r in rows:
    out.append(u"%d\t中四上\t%d\t%d\t%d\t%d\t%d\t%s" % (
        r["n"], r["segs"], r["yi"], r["run"], r["veto"], r["doubt"], r["note"]))
p = os.path.join(ROOT, "batch_qwen", "r7k_done", u"資持記_中四上_b.tsv")
io.open(p, "w", encoding="utf-8", newline="").write("\r\n".join(out) + "\r\n")
print("WROTE", len(rows), "rows")
