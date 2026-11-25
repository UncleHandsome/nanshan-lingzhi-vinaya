# -*- coding: utf-8 -*-
"""把人工補的 orphan 對位回填到 對位結果_20261125/*.jsonl。

輸入 JSONL（每行一筆）：
  {"key":"記段key","A":["鈔段key",...],"type":"1:1|1:n|n:1|n:m|orphan","note":"依據"}
  key 也可寫 "B"；只給 A 就行，type 會自動推。
會依 key 找到它所屬的結果檔，把該行的 A/type/why 換掉。
"""
import glob
import io
import json
import os
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RES = os.path.join(B, '定稿', '對位結果_20261125')


def main():
    if len(sys.argv) < 2:
        print('usage: ingest_orphan_fill.py <filled.jsonl> [--dry]')
        return
    dry = '--dry' in sys.argv
    src = sys.argv[1]
    patches = {}
    for ln in io.open(src, encoding='utf-8'):
        s = ln.strip()
        if not s.startswith('{'):
            continue
        o = json.loads(s)
        k = str(o.get('key') or o.get('B') or '').strip().strip('記鈔 ')
        if not k:
            continue
        a = [str(x).strip().strip('記鈔 ') for x in (o.get('A') or [])]
        patches[k] = {'A': a, 'type': (o.get('type') or '').strip(),
                      'why': (o.get('note') or o.get('why') or '').strip()}
    print('讀到 %d 筆人工對位' % len(patches))
    hit = 0
    for p in sorted(glob.glob(os.path.join(RES, 'pian*.jsonl'))):
        lines = [json.loads(l) for l in io.open(p, encoding='utf-8') if l.strip()]
        changed = 0
        for o in lines:
            k = str(o.get('B') or '').strip()
            if k not in patches:
                continue
            pt = patches[k]
            a = pt['A']
            o['A'] = a
            o['type'] = pt['type'] or ('orphan' if not a else ('1:1' if len(a) == 1 else '1:n'))
            if pt['why']:
                o['why'] = pt['why']
            o['reviewed'] = 'human'
            changed += 1
        if changed:
            hit += changed
            if not dry:
                io.open(p, 'w', encoding='utf-8', newline='\n').write(
                    '\n'.join(json.dumps(o, ensure_ascii=False) for o in lines) + '\n')
            print('  %-34s 更新 %d 筆' % (os.path.basename(p), changed))
    print('共更新 %d 筆%s' % (hit, '（dry-run 未寫入）' if dry else ''))


if __name__ == '__main__':
    main()
