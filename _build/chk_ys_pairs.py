import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\yeshu\卷一.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
pairs = re.findall(r'<div class="pair"[^>]*><div class="o">(.*?)</div><div class="t">(.*?)</div>', body, re.S)
print('pair 數', len(pairs))
for i, (o, t) in enumerate(pairs[:10]):
    o = re.sub('<[^>]+>', '', o).strip()
    t = re.sub('<[^>]+>', '', t).strip()
    print('---', i)
    print('  O:', o[:44])
    print('  T:', t[:44])
