import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for v in ['卷一', '卷二', '卷三', '卷四']:
    h = io.open(B + r'\docs\jieshu\%s.html' % v, encoding='utf-8').read()
    body = h[h.find('<main>'):]
    ms = [(m.group(1), m.start()) for m in re.finditer(r'id="(p\d+)"', body)]
    print('=====', v, '錨點', len(ms), '總 pair', body.count('class="pair"'))
    for pid, pos in ms[:6]:
        n = body[:pos].count('class="pair"')
        txt = re.sub('<[^>]+>', ' ', body[pos:pos + 120])
        txt = re.sub(r'\s+', ' ', txt).strip()
        print('  %-4s pair前%3d | %s' % (pid, n, txt[:52]))
