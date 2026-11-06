import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\jieshu\卷一.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
pairs = re.findall(r'<div class="pair"[^>]*><div class="o">(.*?)</div>', body, re.S)
for i in range(10, 90, 4):
    if i < len(pairs):
        t = re.sub('<[^>]+>', '', pairs[i]).strip()
        print('%3d | %s' % (i, t[:56]))
