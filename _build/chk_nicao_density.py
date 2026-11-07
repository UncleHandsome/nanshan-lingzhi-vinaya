import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\nicao\卷上.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
ps = re.findall(r'<div class="o">(.*?)</div>', body, re.S)
print('原文段', len(ps))
tot = p = 0
for o in ps:
    t = re.sub('<[^>]+>', '', o)
    n = len(re.findall(r'[\u4e00-\u9fff]', t))
    tot += n
    p += len(re.findall(r'[，。、；：？！]', t))
print('總字 %d 標點 %d 密度 %.1f%%' % (tot, p, 100.0 * p / max(1, tot)))
for o in ps[20:24]:
    t = re.sub('<[^>]+>', '', o)
    print(' -', t[:80])
