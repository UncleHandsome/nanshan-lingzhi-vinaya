import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for v in ['卷上', '卷中']:
    h = io.open(B + r'\docs\yichao\%s.html' % v, encoding='utf-8').read()
    body = h[h.find('<main>'):]
    print('=====', v)
    for m in re.finditer(r'id="(p\d+)"', body):
        pid = m.group(1)
        pos = m.start()
        n = body[:pos].count('class="pair"')
        txt = re.sub('<[^>]+>', ' ', body[pos:pos + 120])
        txt = re.sub(r'\s+', ' ', txt).strip()
        print('%-4s 前面 pair %3d | %s' % (pid, n, txt[:46]))
