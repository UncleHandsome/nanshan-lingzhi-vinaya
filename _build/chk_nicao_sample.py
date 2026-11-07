import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\nicao\卷上.html', encoding='utf-8').read()
key = '第一波羅夷者'
i = h.find(key)
print('找到位置', i)
if i > 0:
    seg = re.sub('<[^>]+>', ' ', h[i - 10:i + 420])
    seg = re.sub(r'\s+', ' ', seg)
    print(seg[:360])
else:
    # 找「婆羅夷」
    for k in ['婆羅夷', '僧殘', '偷蘭遮']:
        j = h.find(k)
        print(k, j)
