# -*- coding: utf-8 -*-
import io, os, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(D, '_a008_data.json'), encoding='utf-8'))
J, C = d['ji'], d['cao']
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
JH = [han(x) for x in J]
CH = [han(x) for x in C]

for kw in ['德瓶', '天愍', '非情', '法界', '大千']:
    print('==', kw)
    for c, t in enumerate(CH):
        if kw in t:
            print('  鈔 c=%d %s' % (c, t[max(0, t.find(kw)-30):t.find(kw)+40]))
    for z, t in enumerate(JH):
        if kw in t:
            print('  記 z=%d %s' % (z, t[max(0, t.find(kw)-30):t.find(kw)+40]))

MIN = 4
IDX = {}
for c, t in enumerate(CH):
    seen = set()
    for i in range(len(t) - MIN + 1):
        s = t[i:i+MIN]
        if s in seen: continue
        seen.add(s)
        IDX.setdefault(s, set()).add(c)

def score(z, maxL=40):
    jz = JH[z]; best = {}
    n = len(jz)
    for L in range(min(n, maxL), MIN - 1, -1):
        for i in range(0, n - L + 1):
            s = jz[i:i+L]
            if s in IDX:
                for c in IDX[s]:
                    if best.get(c, 0) < L: best[c] = L
    return best

print('\n--- min4 candidates ---')
for z in [300, 301, 302, 303, 304, 305]:
    b = score(z)
    print(z, sorted(b.items(), key=lambda kv: -kv[1])[:8])
    print('   ji:', JH[z][:60])
