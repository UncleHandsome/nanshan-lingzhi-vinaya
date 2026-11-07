import io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = json.load(io.open(B + r'\docs\nav.json', encoding='utf-8'))
for b in d['books']:
    if b['out'] == 'yeshu':
        for v in b['vols']:
            print(v['v'], [s[1] for s in v['secs']])
h = io.open(B + r'\docs\yeshu\卷一.html', encoding='utf-8').read()
i = h.find('id="p1"')
print('\n--- p1 前後 ---')
print(re.sub('<[^>]+>', ' ', h[max(0, i - 400):i + 300])[:700])
