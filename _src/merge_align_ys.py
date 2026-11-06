# -*- coding: utf-8 -*-
"""合併業疏 AI 對齊（句讀行 i → 分卷行 c）→ hb_align_ys.json"""
import io, os, glob, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ys')


def main():
    out = {}
    for bf in sorted(glob.glob(os.path.join(AD, '[0-9][0-9][0-9].json'))):
        n = os.path.basename(bf)[:3]
        of = os.path.join(AD, 'out_%s.json' % n)
        if not os.path.exists(of):
            continue
        meta = json.load(io.open(bf, encoding='utf-8'))
        key = meta['key']
        d = json.load(io.open(of, encoding='utf-8'))
        arr = {}
        for m in d.get('map', []):
            arr[int(m['i'])] = int(m['c'])
        if not arr:
            continue
        mx = max(arr) + 1
        seq = [0] * mx
        last = 0
        for i in range(mx):
            last = max(last, int(arr.get(i, last)))
            seq[i] = last
        out[key] = seq
    json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align_ys.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('chunks', len(out), 'lines', sum(len(v) for v in out.values()))


if __name__ == '__main__':
    main()
