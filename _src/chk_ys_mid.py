import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\yeshu\卷一.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
pairs = re.findall(r'<div class="pair"[^>]*><div class="o">(.*?)</div><div class="t">(.*?)</div>', body, re.S)
print('pair', len(pairs))
for i in [40, 120, 300, 600, 900, 1200]:
    if i >= len(pairs):
        continue
    o = re.sub('<[^>]+>', '', pairs[i][0]).strip()
    t = re.sub('<[^>]+>', '', pairs[i][1]).strip()
    print('---', i)
    print('  O:', o[:46])
    print('  T:', t[:46])
