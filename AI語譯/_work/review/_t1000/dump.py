# -*- coding: utf-8 -*-
"""Dump each review entry with the current segment text."""
import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'entries.json'), encoding='utf-8'))
ents = d['uniq']

cache = {}
def seg_text(book, chunk, seg):
    key = (book, chunk)
    if key not in cache:
        p = os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt')
        if not os.path.exists(p):
            cache[key] = None
        else:
            t = io.open(p, encoding='utf-8-sig').read()
            cache[key] = [x for x in t.split('\n\n') if x.strip()]
    paras = cache[key]
    if paras is None or seg < 1 or seg > len(paras):
        return None, (len(paras) if paras else 0)
    return paras[seg-1], len(paras)

out = []
for k, e in enumerate(ents, 1):
    txt, n = seg_text(e['book'], e['chunk'], e['seg'])
    out.append('=' * 100)
    out.append('### [%02d] %s | %s | %s | segs=%s' % (k, e['gid'], e['level'], e['cat'], n))
    out.append('原文起首：' + e['orig'])
    if e['problem']:
        out.append('問題：' + e['problem'])
    if e['basis']:
        out.append('依據：' + e['basis'])
    if e['suggestion']:
        out.append('建議：' + e['suggestion'])
    if e['doubt']:
        out.append('存疑：' + e['doubt'])
    out.append('信心：' + e['conf'])
    out.append('- - - 現行第 %d 段（%s 字） - - -' % (e['seg'], len(txt) if txt else 'NA'))
    out.append(txt if txt is not None else '<<<SEG NOT FOUND>>>')
    out.append('')

io.open(os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'dump.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('dumped', len(ents))
