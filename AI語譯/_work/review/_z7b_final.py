# -*- coding: utf-8 -*-
import io, os
rows = [l.rstrip("\n") for l in io.open("_z7b_rows.tsv", encoding="utf-8") if l.strip()]
print("rows", len(rows))
tot = [0,0,0,0,0]
for r in rows:
    f = r.split("\t")
    print(f[0], "segs=%s yi=%s run=%s veto=%s doubt=%s" % tuple(f[2:7]))
    for i,k in enumerate(range(2,7)):
        tot[i] += int(f[k])
print("TOTAL segs=%d yi=%d run=%d veto=%d doubt=%d" % tuple(tot))
hdr = u"檔號\t卷\t改段數\t義理修正\t潤飾\t否決\t存疑\t備註\n"
out = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r7k_done\資持記_中三下_b.tsv"
with io.open(out, "w", encoding="utf-8", newline="") as f:
    f.write(hdr + u"\n".join(rows) + u"\n")
print("wrote", out, os.path.getsize(out))
# doubt append
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\存疑材料\7K_存疑.md"
add = u"11. **1784-0001／10d#37「未受食污手」**：可讀作「食物尚未入口就弄髒手」，亦可讀作與「受食法」有關；現從前讀，待核鈔文。\n12. **1785-0001／10d#45「通開可成」**：主賓語未明（因病通開諸戒，故為病者說法得成？），現依文理補足，待核《行事鈔》原句。\n13. **1785-0007／11a#3「上二字／下四字」**：所指六字為何，須核鈔文原句才能鎖定，現只依科文層次（就上句而言）譯出。\n"
with io.open(p, "a", encoding="utf-8") as f:
    f.write(add)
print("doubt appended")
