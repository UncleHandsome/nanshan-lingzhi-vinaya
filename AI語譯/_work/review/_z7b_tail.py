# -*- coding: utf-8 -*-
import io, os
# 1) append 1780 row to official TSV
tsv = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r7k_done\資持記_中三下_b.tsv"
row = u"1780\t中三下\t7\t11\t5\t5\t1\t人所嫌／喜生蟲不增字、三種材料、蒲臺＝花穗、他施棄而用之從簡、指緣同上白話化、寶藥＝捉寶戒＋畜藥戒、二義點明、牙角句＝做他物非做筒、雜字保留原字（𥎞／𮢏）、十二為項非「十二律」、他曆反給今音、增一尺＝長頭廣邊、兩重＝摺疊；否決：柳紫改絮出注、鉢改針出注、七改匕出注、鏢𥎞改鐓出注、《多論》《寄歸傳》《感通傳》補全稱；存疑：0002「他施棄而用之」兩讀\n"
with io.open(tsv, "a", encoding="utf-8", newline="") as f:
    f.write(row)
# 2) append doubt item 10
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\存疑材料\7K_存疑.md"
add = u"10. **1780-0002／10d#10「若他施棄而用之」**：一讀「他人施與之物，棄除（兜羅）後再用」，一讀「他人施捨丟棄之物，取來用」；現從前讀，較保守。\n"
with io.open(p, "a", encoding="utf-8") as f:
    f.write(add)
print("ok", os.path.getsize(tsv))
