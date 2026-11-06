import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for v in ['卷一', '卷二', '卷三', '卷四']:
    h = io.open(B + r'\docs\yeshu\%s.html' % v, encoding='utf-8').read()
    b = h[h.find('<main>'):]
    ps = re.findall(r'<div class="o">(.*?)</div>', b, re.S)
    tot = p = no = 0
    for o in ps:
        t = re.sub('<[^>]+>', '', o)
        n = len(re.findall(r'[\u4e00-\u9fff]', t))
        tot += n
        p += len(re.findall(r'[，。、；：？！]', t))
        if n > 20 and not re.search(r'[，。、；：？！]', t):
            no += 1
    print('%s 段%d 密度%.1f%% 無標點段%d' % (v, len(ps), 100.0 * p / max(1, tot), no))
