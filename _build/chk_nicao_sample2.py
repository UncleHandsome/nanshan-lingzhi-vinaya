import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\nicao\卷上.html', encoding='utf-8').read()
for k in ['波羅夷', '夷者', '十誦云']:
    print(k, h.find(k))
i = h.find('偷蘭遮')
seg = re.sub('<[^>]+>', ' ', h[i - 200:i + 500])
print(re.sub(r'\s+', ' ', seg)[:400])
