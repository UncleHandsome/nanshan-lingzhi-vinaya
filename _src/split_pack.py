# -*- coding: utf-8 -*-
"""把打包組的譯文按 [1][2]… 拆回原段落。

用法：
  python -X utf8 _src/split_pack.py --batch 測試/實驗11/_L7_盲翻
"""
import argparse
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', required=True)
    ap.add_argument('--materials', default='')
    ap.add_argument('--out', default='')
    args = ap.parse_args()

    base = os.path.join(B, args.batch.replace('/', os.sep))
    mdir = os.path.join(B, args.materials.replace('/', os.sep)) if args.materials else base
    rep = os.path.join(base, '回覆')
    out = os.path.join(B, args.out.replace('/', os.sep)) if args.out else os.path.join(base, '_分段')
    os.makedirs(out, exist_ok=True)

    ok = bad = 0
    for fn in sorted(os.listdir(mdir)):
        if not fn.endswith('.json'):
            continue
        key = fn[:-5]
        d = json.load(io.open(os.path.join(mdir, fn), encoding='utf-8'))
        if not isinstance(d, dict) or not d.get('packed'):
            continue
        need = len(d.get('segments') or [])
        rp = os.path.join(rep, key + '_回.txt')
        if not os.path.exists(rp):
            rp = os.path.join(base, key + '.txt')
        if not need or not os.path.exists(rp):
            bad += 1
            continue
        txt = io.open(rp, encoding='utf-8').read()
        txt = re.sub(r'^\s*【(?:疏文|記文|鈔文|律文|註文|序文)】\s*\n?', '', txt)
        parts = re.split(r'\[\s*(\d+)\s*\]', txt)
        segs = [(int(parts[i]), parts[i + 1].strip())
                for i in range(1, len(parts) - 1, 2)]
        if len(segs) != need:
            print('  ⚠ 段數不符：%s（需要 %d，實得 %d）' % (key, need, len(segs)))
            bad += 1
            continue
        for n, body in segs:
            io.open(os.path.join(out, '%s_%02d.txt' % (key, n)), 'w',
                    encoding='utf-8').write(body + '\n')
        ok += 1
    print('拆回完成：%d 組成功、%d 組異常 → %s' % (ok, bad, os.path.relpath(out, B)))


if __name__ == '__main__':
    main()
