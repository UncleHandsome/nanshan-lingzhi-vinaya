import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\nicao\卷上.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
pairs = re.findall(r'<div class="pair"[^>]*><div class="o">(.*?)</div>', body, re.S)
print('pair 數', len(pairs))
bad = []
for i, o in enumerate(pairs):
    t = re.sub('<[^>]+>', '', o)
    n = len(t)
    p = len(re.findall(r'[，。、；：？！]', t))
    if n > 20 and p == 0:
        bad.append((i, t[:40]))
print('無標點段落數', len(bad))
for b in bad[:8]:
    print('  ', b)
