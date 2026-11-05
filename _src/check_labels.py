# -*- coding: utf-8 -*-
"""檢查四層標籤套用結果與 layers.json 是否一致。"""
import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
LAB = {'律': '律文', '註': '註文', '疏': '疏文', '記': '記文'}
LEAD = re.compile(r'^【([^】]+)】')


def paras(p):
    return [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def main(book):
    layers = json.load(io.open(os.path.join(B, 'AI語譯', 'layers', book + '.json'), encoding='utf-8'))
    T = os.path.join(B, 'AI語譯', 'out', book)
    ok = bad = 0
    dist = {}
    samples = []
    for key, lay in layers.items():
        p = os.path.join(T, key + '.txt')
        if not os.path.exists(p):
            continue
        ps = paras(p)
        for i, seg in enumerate(ps):
            m = LEAD.match(seg)
            lab = m.group(1) if m else ''
            want = LAB.get(lay[i], '')
            dist[lab or '(none)'] = dist.get(lab or '(none)', 0) + 1
            if lab == want:
                ok += 1
            else:
                bad += 1
                if len(samples) < 15:
                    samples.append((key, i + 1, lay[i], lab, seg[:40]))
    print(book, 'ok', ok, 'bad', bad)
    print('  dist', dist)
    for s in samples:
        print('  !!', s)


if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else '02_戒疏')
