import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\yichao\卷上.html', encoding='utf-8').read()
body = h[h.find('<main>'):]
# 依 pair 順序抽文字
segs = re.findall(r'<div class="pair" id="(s\d+|p\d+)"><div class="[ot]2?">(.*?)</div>', body, re.S)
print('pair 數', len(segs))
for i, (pid, txt) in enumerate(segs[:22]):
    t = re.sub('<[^>]+>', '', txt)
    print('%-4s %s' % (pid, t[:40]))
print('p1 之前 pair 數', body[:body.find('id="p1"')].count('class="pair"'))
