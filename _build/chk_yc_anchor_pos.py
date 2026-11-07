import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\yichao\卷上.html', encoding='utf-8').read()
for pid in ['p1', 'p2', 'p16']:
    i = h.find('id="%s"' % pid)
    if i < 0:
        print(pid, '不存在')
        continue
    print(pid, '前面 pair 數', h[:i].count('class="pair"'), '|',
          re.sub('<[^>]+>', ' ', h[i:i + 160])[:80])
