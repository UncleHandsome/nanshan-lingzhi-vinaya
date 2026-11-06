import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for v in ['卷二', '卷四']:
    h = io.open(B + r'\docs\yeshu\%s.html' % v, encoding='utf-8').read()
    body = h[h.find('<main>'):]
    for m in re.finditer(r'<h2 class="sec" id="(p\d+)">([^<]+)</h2>', body):
        pid, name = m.group(1), m.group(2)
        n = body[:m.start()].count('class="pair"')
        print('%s %-10s pair前%4d' % (v, name, n))
