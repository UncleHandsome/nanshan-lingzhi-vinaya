import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in ['docs/yichao/卷上.html', 'docs/yichao/卷中.html', 'docs/nicao/卷中.html', 'docs/nicao/卷下.html']:
    h = io.open(B + '\\' + f.replace('/', '\\'), encoding='utf-8').read()
    b = h[h.find('<main>'):]
    ps = re.findall(r'<div class="o">(.*?)</div>', b, re.S)
    tot = p = 0
    for o in ps:
        t = re.sub('<[^>]+>', '', o)
        tot += len(re.findall(r'[\u4e00-\u9fff]', t))
        p += len(re.findall(r'[，。、；：？！]', t))
    print(f, '段', len(ps), '密度 %.1f%%' % (100.0 * p / max(1, tot)))
