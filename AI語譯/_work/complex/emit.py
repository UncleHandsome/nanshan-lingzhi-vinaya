# -*- coding: utf-8 -*-
"""Emit fix_complex.tsv, 判定_complex.tsv and 說明_complex.md."""
import json, os, re, sys, collections, glob
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
REV = os.path.join(ROOT, 'AI語譯', '_work', 'review')
BAK = os.path.join(ROOT, '歸檔', 'complex批修正前')

def read_blocks(p):
    raw = open(p, 'rb').read().decode('utf-8')
    eol = '\r\n' if '\r\n' in raw else '\n'
    return [b for b in re.split(re.escape(eol + eol), raw)], eol

def main():
    os.makedirs(REV, exist_ok=True)
    # 1. collect changed segments by diffing backup vs current
    fixes = []
    for f in sorted(glob.glob(os.path.join(BAK, '**', '*.txt'), recursive=True)):
        book = os.path.basename(os.path.dirname(f))
        chunk = os.path.splitext(os.path.basename(f))[0]
        cur = os.path.join(ROOT, 'AI語譯', 'out', book, chunk + '.txt')
        if not os.path.exists(cur):
            continue
        a, _ = read_blocks(f)
        b, _ = read_blocks(cur)
        if len(a) != len(b):
            print('COUNT DIFF', book, chunk)
            continue
        for i, (x, y) in enumerate(zip(a, b), 1):
            if x != y:
                fixes.append((book, chunk, i, y))
    with open(os.path.join(REV, 'fix_complex.tsv'), 'w', encoding='utf-8') as f:
        for book, chunk, seg, new in fixes:
            f.write('%s\t%s\t%d\t%s\n' % (book, chunk, seg, new.replace('\n', '\\n')))
    print('fix rows', len(fixes))

    B = json.load(open(os.path.join(OUT, 'build.json'), encoding='utf-8'))
    dec = B['decisions']
    st = collections.Counter(d['verdict'] for d in dec)
    fp = collections.Counter(d['cat'] for d in dec if d['verdict'] == '誤報')
    deferred = [d for d in dec if d['verdict'] == '真錯' and d['cat'] == '待套用']
    applied_tags = set()
    for book, chunk, seg, new in fixes:
        applied_tags.add('%s#%d' % (chunk, seg))

    # decision tsv
    with open(os.path.join(REV, '判定_complex.tsv'), 'w', encoding='utf-8') as f:
        f.write('項次\t書/chunk#段\t級\t類型\t判定\t誤報分類\t備註\n')
        for i, d in enumerate(dec, 1):
            lab = d['label']
            m = re.match(r'(.+?)/([^/]+)#(\d+)$', lab)
            key = '%s#%s' % (m.group(2), m.group(3)) if m else lab
            note = '已套用' if (d['verdict'] == '真錯' and d['cat'] != '待套用') else (d['note'] or '')
            f.write('%d\t%s\t%s\t%s\t%s\t%s\t%s\n' % (i, lab, d['pl'], (d['type'] or '').replace(chr(10),' ')[:30],
                                                       d['verdict'], d['cat'], note))
    print('decision rows', len(dec))
    json.dump({'fixes': len(fixes), 'st': dict(st), 'fp': dict(fp),
               'deferred': len(deferred), 'dec': len(dec)},
              open(os.path.join(OUT, 'final_stats.json'), 'w', encoding='utf-8'), ensure_ascii=False)

if __name__ == '__main__':
    main()
