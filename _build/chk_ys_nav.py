import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
h = io.open(B + r'\docs\yeshu\卷一.html', encoding='utf-8').read()
hs = re.findall(r'<h2 class="sec" id="(p\d+)">([^<]+)</h2>', h)
print('h2 錨點', len(hs))
for x in hs[:12]:
    print('  ', x)
toc = re.findall(r'#p(\d+)">([^<]+)</a>', h)
print('側欄連結（去重前 12）:')
for x in toc[:12]:
    print('  ', x)
# 錨點是否真的存在
for pid, name in hs[:5]:
    print(pid, '存在於頁面:', ('id="%s"' % pid) in h)
