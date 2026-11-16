# -*- coding: utf-8 -*-
"""打包單位的定稿與拆回。

用法：
  python -X utf8 _src/pack_final.py --pack 測試/_pack_審核 --revise 測試/_pack_修訂 --out 測試/_pack_定稿
"""
import argparse
import io
import json
import os
import re
import norm

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'


def split_marked(text, n):
    _head = ''
    _mh = re.match(r'\s*(【(?:疏文|記文|鈔文|律文|註文|序文)】)\s*', text)
    if _mh:
        _head = _mh.group(1)
        text = text[_mh.end():]
    parts = re.split(r'(?m)^\s*`?\s*(?:[-*•]|\d+[.、])?\s*\[\s*(\d+)\s*\]\s*', text)
    segs = [(int(parts[i]), parts[i + 1].strip())
            for i in range(1, len(parts) - 1, 2)]
    if len(segs) != n:
        _labm = re.findall(r'【(疏文|記文|鈔文|律文|註文|序文)】([\s\S]*?)(?=【(?:疏文|記文|鈔文|律文|註文|序文)】|\Z)', text)
        if _labm:
            _per = {}
            for _lb, _body in _labm:
                _pp = re.split(r'(?m)^\s*\[\s*(\d+)\s*\]\s*', _body)
                for _ii in range(1, len(_pp) - 1, 2):
                    _per.setdefault(int(_pp[_ii]), []).append((_lb, _pp[_ii + 1].strip()))
            if len(_per) == n:
                return ['\n\n'.join('【%s】\n%s' % (a, b) for a, b in _per[i])
                        for i in sorted(_per)]
        return None
    out = [b for _, b in sorted(segs)]
    if _head:
        out = [(_head + '\n' + b) if not re.match(r'【', b) else b for b in out]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pack', required=True)
    ap.add_argument('--revise', default='')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    pk = os.path.join(B, args.pack.replace('/', os.sep))
    rv = os.path.join(B, args.revise.replace('/', os.sep)) if args.revise else ''
    out = os.path.join(B, args.out.replace('/', os.sep))
    os.makedirs(out, exist_ok=True)

    mp = json.load(io.open(os.path.join(pk, '索引_pack.json'), encoding='utf-8'))
    ok = bad = 0
    for key, members in mp.items():
        body = ''
        rp = os.path.join(rv, '回覆', key + '_回.txt') if rv else ''
        if rp and os.path.exists(rp):
            body = io.open(rp, encoding='utf-8').read().strip()
        if not body:
            md = os.path.join(pk, key + '.md')
            if os.path.exists(md):
                t = io.open(md, encoding='utf-8').read()
                i = t.find('【待審譯文】')
                j = t.find('【後文背景', i)
                body = t[i + len('【待審譯文】'):j if j > 0 else None].strip()
        if len(members) == 1:
            body = re.sub(r'^\[\d+\]\s*', '', body).strip()
            io.open(os.path.join(out, members[0] + '.txt'), 'w',
                    encoding='utf-8').write(body + '\n')
            ok += 1
            continue
        segs = split_marked(body, len(members))
        if not segs:
            print('  ⚠ 段數不符，整包輸出：', key)
            io.open(os.path.join(out, key + '_未拆.txt'), 'w',
                    encoding='utf-8').write(body + '\n')
            bad += 1
            continue
        for m, seg in zip(members, segs):
            seg = re.sub(r'^\[\d+\]\s*', '', seg).strip()
            io.open(os.path.join(out, m + '.txt'), 'w', encoding='utf-8').write(norm.normalize(seg) + '\n')
        ok += 1
    print('拆回：%d 包成功、%d 包異常 → %s' % (ok, bad, os.path.relpath(out, B)))


if __name__ == '__main__':
    main()
