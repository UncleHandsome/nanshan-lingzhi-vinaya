import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\jieshu\卷一.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
pairs = re.findall(r'<div class="pair"[^>]*><div class="o">(.*?)</div>', body, re.S)
print('pairs', len(pairs))
for i in [0, 30, 100, 300, 700, 1200, 1800]:
    if i < len(pairs):
        t = re.sub('<[^>]+>', '', pairs[i]).strip()
        print(i, '|', t[:60])
