import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\yeshu\卷一.html', encoding='utf-8').read()
for pid in ['p1']:
    i = h.find('<h2 class="sec" id="%s"' % pid)
    seg = h[i:i + 700]
    txt = re.sub('<[^>]+>', ' ', seg)
    print(pid, '→', txt[:300])
# 統計 p1 前面有幾個 pair
j = h.find('id="p1"')
print('p1 之前 pair 數', h[:j].count('class="pair"'))
