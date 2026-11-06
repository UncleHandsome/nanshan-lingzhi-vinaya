# -*- coding: utf-8 -*-
"""對 z=300..470 的記段，找出與各鈔段的最長共同子串（>=5字），列出候選。"""
import io, os, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(D, '_a008_data.json'), encoding='utf-8'))
J, C = d['ji'], d['cao']
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
JH = [han(x) for x in J]
CH = [han(x) for x in C]
print('cao lens:', sorted(len(x) for x in CH)[:5], '...', sorted(len(x) for x in CH)[-5:])
print('cao total', sum(len(x) for x in CH), 'ji total', sum(len(x) for x in JH))

# 建立 鈔 的索引：所有 >=6 字的子串 -> set of c
IDX = {}
MIN = 6
for c, t in enumerate(CH):
    seen = set()
    for i in range(len(t) - MIN + 1):
        s = t[i:i+MIN]
        if s in seen:
            continue
        seen.add(s)
        IDX.setdefault(s, set()).add(c)

def score(z):
    jz = JH[z]
    best = {}
    n = len(jz)
    for L in range(min(n, 40), MIN - 1, -1):
        for i in range(0, n - L + 1):
            s = jz[i:i+L]
            if s in IDX:
                for c in IDX[s]:
                    if best.get(c, 0) < L:
                        best[c] = L
        # 保留較長者即可，不 break（同段可能有多處引文）
    return best

out = []
for z in range(295, 470):
    b = score(z)
    top = sorted(b.items(), key=lambda kv: -kv[1])[:6]
    out.append((z, top))
    print('%3d | %s' % (z, ' '.join('c%d:%d' % (c, L) for c, L in top)))
json.dump({str(z): top for z, top in out}, io.open(os.path.join(D, '_a008_match.json'), 'w', encoding='utf-8'), ensure_ascii=False)
