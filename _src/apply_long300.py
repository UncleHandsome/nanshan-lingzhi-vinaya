# -*- coding: utf-8 -*-
"""套用單段 >300 字的 Qwen 拆分回覆，只切指定的 segment。"""
import argparse
import glob
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '單段300_待拆')
OUT = os.path.join(ROOT, 'AI輸出')


def load_rows(book):
    p = os.path.join(B, '定稿', book + '.jsonl')
    return [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]


def parse(o):
    seg = int(o.get('segment') or 0)
    parts = o.get('parts') or []
    if seg < 1 or not parts:
        return None, 'bad segment/parts'
    out = []
    for p in parts:
        h = re.sub(r'^【[^】]+】\s*', '', str(p.get('head') or '').strip())
        tr = str(p.get('translation') or '').strip()
        if not h or not tr:
            return None, 'bad head/translation'
        out.append((h, tr))
    return (seg, out), ''


def norm_map(s):
    out=[]; idx=[]
    for i,ch in enumerate(s):
        if not ch.isspace() and ch != '\u3000':
            out.append(ch); idx.append(i)
    return ''.join(out), idx


def split_segment(seg, parts):
    ss = (seg.get('display_source') or seg.get('source') or '').strip()
    if not ss:
        return None, 'empty source'
    ns, nmap = norm_map(ss)
    pos = []
    for j, (h, tr) in enumerate(parts):
        nh, _ = norm_map(h)
        idx = ns.find(nh)
        if idx < 0:
            return None, 'head not found: ' + h[:16]
        if ns.find(nh, idx + 1) >= 0:
            return None, 'head not unique: ' + h[:16]
        raw = nmap[idx]
        if j == 0 and raw != 0:
            # 第一段白話仍涵蓋開頭；把起點拉回 0
            raw = 0
        if pos and raw <= pos[-1]:
            return None, 'head order'
        pos.append(raw)
    new = []
    for j, (h, tr) in enumerate(parts):
        a = pos[j]; b = pos[j + 1] if j + 1 < len(parts) else len(ss)
        s2 = dict(seg)
        s2['source'] = ss[a:b]
        s2['display_source'] = ss[a:b]
        s2['translation'] = tr
        new.append(s2)
    return new, ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    changed = {}; ok = bad = 0
    for p in glob.glob(os.path.join(OUT, '*_回.txt')):
        s = io.open(p, encoding='utf-8').read().strip()
        if not s or s.upper() == 'NONE':
            bad += 1; print('SKIP', os.path.basename(p), 'NONE/empty'); continue
        try:
            o = json.loads(s.splitlines()[0])
        except Exception as e:
            bad += 1; print('SKIP', os.path.basename(p), 'json', e); continue
        book = o.get('book_id'); key = str(o.get('key') or '')
        if '／' in key: key = key.rsplit('／', 1)[-1]
        elif '/' in key: key = key.rsplit('/', 1)[-1]
        parsed, err = parse(o)
        if not parsed:
            bad += 1; print('SKIP', book, key, err); continue
        segno, parts = parsed
        rows = load_rows(book); by = {str(r['key']): r for r in rows}
        r = by.get(key)
        if not r:
            bad += 1; print('SKIP missing', book, key); continue
        segs = r.get('segments') or []
        if segno > len(segs):
            bad += 1; print('SKIP segno', book, key, segno); continue
        new, err = split_segment(segs[segno - 1], parts)
        if not new:
            bad += 1; print('SKIP', book, key, err); continue
        changed[(book, key)] = (segno, new)
        print('OK', book, key, 'seg', segno, 'parts', len(new))
        ok += 1
    if a.apply and changed:
        for book in {b for b, _ in changed}:
            path = os.path.join(B, '定稿', book + '.jsonl')
            shutil.copy2(path, os.path.join(B, '定稿', '_舊_%s_before_long300_20261124.jsonl' % book))
            rows = load_rows(book); by = {str(r['key']): r for r in rows}
            for (b, k), (segno, new) in changed.items():
                if b != book or k not in by: continue
                r = by[k]; segs = r.get('segments') or []
                r['segments'] = segs[:segno - 1] + new + segs[segno:]
                r['translation'] = '\n\n'.join((s.get('translation') or '') for s in r['segments'])
            io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
                json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
    print('ok', ok, 'bad', bad)


if __name__ == '__main__':
    main()
