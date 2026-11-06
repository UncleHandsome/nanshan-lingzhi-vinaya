# -*- coding: utf-8 -*-
"""以「篇名」對齊合併所有 AI 對齊批次（避免 sec 編號偏移）"""
import io, os, glob, json, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)

SECS = ex.sections()
NAME2IDX = {}
for i, s in enumerate(SECS):
    NAME2IDX.setdefault(s['name'], i)

DIRS = ['align_ai', 'align_fix', 'align_last3']


def main():
    maps = {}
    by_name = {}
    for d in DIRS:
        p = os.path.join(B, 'AI語譯', '_work', d)
        if not os.path.isdir(p):
            continue
        for bf in sorted(glob.glob(os.path.join(p, '[0-9][0-9][0-9].json'))):
            b = json.load(io.open(bf, encoding='utf-8-sig'))
            name = b.get('name')
            if name not in NAME2IDX:
                print('!! 篇名對不上', name, os.path.basename(bf))
                continue
            n = os.path.basename(bf)[:3]
            of = os.path.join(p, 'out_%s.json' % n)
            if not os.path.exists(of):
                continue
            o = json.load(io.open(of, encoding='utf-8-sig'))
            idx = NAME2IDX[name]
            for m in o.get('map', []):
                maps.setdefault(idx, {})[int(m['z'])] = int(m['c'])
    out = {}
    for idx, d in maps.items():
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
        out[str(idx)] = arr
    json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('篇', len(out))
    for k in sorted(out, key=int):
        print('  篇%-3d %-8s 對齊 %d 段' % (int(k) + 1, SECS[int(k)]['name'], len(out[k])))


if __name__ == '__main__':
    main()
