import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\yeshu\卷一.html', encoding='utf-8').read()
b = h[h.find('<main>'):]
ps = re.findall(r'<div class="o">(.*?)</div>', b, re.S)
tags = 0
for o in ps:
    t = re.sub('<[^>]+>', '', o).strip()
    if t.startswith('【'):
        tags += 1
print('原文段', len(ps), '有【標記', tags)
for o in ps[4:8]:
    print(re.sub('<[^>]+>', '', o)[:44])
