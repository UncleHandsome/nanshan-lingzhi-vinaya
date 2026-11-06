import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\jieshu\卷一.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
pairs = re.findall(r'<div class="pair"[^>]*><div class="o">(.*?)</div>', body, re.S)
for i, o in enumerate(pairs):
    t = re.sub('<[^>]+>', '', o).strip()
    if re.match(r'^【(疏|律)】\s*(初篇|二篇|三篇|四篇|五篇|四波羅夷|十三僧殘|二不定|三十捨墮|九十單提|四提舍尼|眾學|七滅諍)', t):
        print(i, '|', t[:50])
