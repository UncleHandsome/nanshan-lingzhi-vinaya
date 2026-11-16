# -*- coding: utf-8 -*-
"""把長段小段的譯文拼回母段。

用法：
  python -X utf8 _src/merge_long.py --book 行事鈔
"""
import argparse
import io
import json
import re
import os
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))


def _clean(seg):
    return re.sub(r'^\s*\**\s*【(?:疏文|記文|鈔文|律文|註文|序文)】\s*\**\s*', '', seg).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True)
    args = ap.parse_args()

    root = os.path.join(B, '測試', '重譯', args.book, '_長段')
    mp = os.path.join(root, '_對應.json')
    if not os.path.exists(mp):
        print('找不到對應表：', mp)
        return
    mapping = json.load(io.open(mp, encoding='utf-8'))
    rep = os.path.join(root, '_盲翻', '回覆')
    out = os.path.join(root, '_定稿')
    os.makedirs(out, exist_ok=True)

    groups = {}
    for m in mapping:
        groups.setdefault((m['chunk'], m['idx']), []).append(m)

    done = miss = 0
    for (chunk, idx), parts in sorted(groups.items()):
        parts.sort(key=lambda x: x['part'])
        segs = []
        ok = True
        for i_p, p in enumerate(parts):
            fp = os.path.join(rep, p['file'].replace('.md', '_回.txt'))
            if not os.path.exists(fp):
                ok = False
                break
            seg = io.open(fp, encoding='utf-8').read().strip()
            if i_p > 0:
                seg = _clean(seg)
            segs.append(seg)
        if not ok:
            miss += 1
            continue
        body = ''
        for _s in segs:
            if body and re.match(r'^(?:[問答][：:]|[一二三四五六七八九十]+、|（[一二三四五六七八九十]+）)', _s):
                body += '\n'
            body += _s
        io.open(os.path.join(out, '%s_L%04d.txt' % (chunk, idx + 1)), 'w',
                encoding='utf-8').write(body)
        done += 1

    print('%s：長段拼回 %d 個母段、缺 %d → %s'
          % (args.book, done, miss, os.path.relpath(out, B)))


if __name__ == '__main__':
    main()
