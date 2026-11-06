# -*- coding: utf-8 -*-
"""合併兩批 AI 對齊結果 → hb_align.json"""
import io, os, re, json, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai')
AD2 = os.path.join(B, 'AI語譯', '_work', 'align_ai2')


def collect(dirpath):
    meta = {}
    for f in sorted(glob.glob(os.path.join(dirpath, '[0-9][0-9][0-9].json'))):
        if f.endswith('manifest.json'):
            continue
        d = json.load(io.open(f, encoding='utf-8'))
        for it in d.get('items', []):
            meta[it['z']] = d['sec']
    maps = {}
    for f in sorted(glob.glob(os.path.join(dirpath, 'out_*.json'))):
        d = json.load(io.open(f, encoding='utf-8'))
        for m in d.get('map', []):
            z, c = int(m['z']), int(m['c'])
            s = meta.get(z)
            if s is None:
                continue
            maps.setdefault(s, {})[z] = c
    return maps


def main():
    maps = collect(AD)
    if os.path.isdir(AD2):
        m2 = collect(AD2)
        for s, d in m2.items():
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
    for s, arr in sorted(out.items(), key=lambda x: int(x[0])):
        print('  篇%-3d 對齊 %d 段' % (int(s) + 1, len(arr)))


if __name__ == '__main__':
    main()
