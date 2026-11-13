# -*- coding: utf-8 -*-
import io
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r7k_done\資持記_上一上.tsv"
t = io.open(p, encoding="utf-8", newline="").read()
a = u"1342\t上一上\t4\t"
b = u"1342\t上一上\t3\t"
c = u"1344\t上一上\t5\t"
d = u"1344\t上一上\t4\t"
assert t.count(a) == 1 and t.count(c) == 1, (t.count(a), t.count(c))
t = t.replace(a, b).replace(c, d)
io.open(p, "w", encoding="utf-8", newline="").write(t)

q = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\交接_7K_資持記上一上_續2.md"
s = io.open(q, encoding="utf-8", newline="").read()
s2 = s.replace(u"25 檔、改 **138 段**", u"25 檔、改 **136 段**").replace(u"（義理修正 220 處、潤飾 252 處）", u"（義理修正 220 處、潤飾 253 處）")
assert s2 != s
io.open(q, "w", encoding="utf-8", newline="").write(s2)
print("patched")
