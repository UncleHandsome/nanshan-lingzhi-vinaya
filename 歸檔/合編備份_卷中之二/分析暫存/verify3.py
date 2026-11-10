# -*- coding: utf-8 -*-
import io, re, html
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
h = io.open(B + r"\docs\hebian\卷中之二.html", encoding="utf-8").read()
# 取 pair 的 o 段
items = re.findall(r'<div class="(o2|o)">(.*?)</div><div class="t">', h, re.S)
print('pairs', len(items))
for i,(cls,txt) in enumerate(items[:6] + items[18:26], 0):
    print(i, cls, html.unescape(txt)[:44])
# 註：index 對應
seq = [(cls, html.unescape(txt)) for cls, txt in items]
# 找 記385 與 鈔68 的相對位置
k385 = [i for i,(c,t) in enumerate(seq) if t.startswith('【記】為他下，釋出其相。')]
k68 = [i for i,(c,t) in enumerate(seq) if t.startswith('【鈔】摩觸女人戒第二。')]
print('記385 at', k385, '鈔68 at', k68)
print('h2 sections:', re.findall(r'<h2 class="sec"[^>]*>(.*?)</h2>', h))
