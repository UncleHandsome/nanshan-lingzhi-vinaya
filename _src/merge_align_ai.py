# -*- coding: utf-8 -*-
"""合併兩批 AI 對齊結果 → hb_align.json（以批次檔的 sec 為準，避免 z 撞號）"""
import io, os, glob, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai')
AD2 = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
AD3 = os.path.join(B, 'AI語譯', '_work', 'align_ys')


def collect(dirpath):
    maps = {}
    for bf in sorted(glob.glob(os.path.join(dirpath, '[0-9][0-9][0-9].json'))):
        n = os.path.basename(bf)[:3]
        out = os.path.join(dirpath, 'out_%s.json' % n)
        if not os.path.exists(out):
            continue
        meta = json.load(io.open(bf, encoding='utf-8'))
        sec = meta.get('sec')
        if sec is None:
            continue
        d = json.load(io.open(out, encoding='utf-8'))
        for m in d.get('map', []):
            maps.setdefault(sec, {})[int(m['z'])] = int(m['c'])
    return maps


def main():
    maps = collect(AD)
    for extra in (AD2 if os.path.isdir(AD2) else None,):
        if extra:
            for s, d in collect(extra).items():
                maps.setdefault(s, {}).update(d)
    out = {}
    for s, d in maps.items():
        mx = max(d) + 1
        arr = [None] * mx
        for z, c in d.items():
            arr[z] = c
        last = 0
        for i in range(mx):
            if arr[i] is None:
                arr[i] = last
            arr[i] = max(last, int(arr[i]))
            last = arr[i]
        out[str(s - 1)] = arr
    json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('篇', len(out), '記段', sum(len(v) for v in out.values()))
    print('篇號:', sorted(int(k) + 1 for k in out))


if __name__ == '__main__':
    main()
