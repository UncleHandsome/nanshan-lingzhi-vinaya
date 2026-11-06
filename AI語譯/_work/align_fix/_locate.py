# -*- coding: utf-8 -*-
"""Locate each align_fix batch's items in 資持記_細分 and cand in 01_行事鈔."""
import io, json, os, re, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def load(sub):
    S = os.path.join(B, 'TXT_分卷', sub)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        lines = io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')
        for ln in lines[5:]:
            ln = ln.strip()
            if ln:
                out.append((f, ln))
    return out


def find(seq, text, used_after=-1):
    """find index >= used_after+1 whose paragraph startswith text[:16] (or contains)"""
    key = text[:16]
    keyh = han(text)[:16]
    for i in range(used_after + 1, len(seq)):
        p = seq[i][1]
        if p.startswith(key):
            return i, 'prefix'
    for i in range(used_after + 1, len(seq)):
        p = seq[i][1]
        if keyh and keyh in han(p):
            return i, 'hansub'
    return -1, 'none'


def run(batch):
    d = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'align_fix', batch), encoding='utf-8'))
    Z = load('資持記_細分')
    C = load('01_行事鈔')
    out = io.StringIO()
    out.write('##### %s sec=%s name=%s items=%d cand=%d\n' % (batch, d['sec'], d['name'], len(d['items']), len(d['cand'])))
    last = -1
    out.write('--- ITEMS ---\n')
    for it in d['items']:
        i, how = find(Z, it['text'], last)
        if i >= 0:
            last = i
        out.write('z=%-3d %s %s  len=%d  [%s]\n' % (it['z'], ('@%d' % i) if i >= 0 else '@??', how,
                                                    len(it['text']), (Z[i][1][:60] if i >= 0 else it['text'][:60])))
    last = -1
    out.write('--- CAND ---\n')
    for c in d['cand']:
        i, how = find(C, c['text'], last)
        if i >= 0:
            last = i
        out.write('c=%-3d %s %s  len=%d  [%s]\n' % (c['c'], ('@%d' % i) if i >= 0 else '@??', how,
                                                    len(c['text']), (C[i][1][:60] if i >= 0 else c['text'][:60])))
    return out.getvalue()


for b in ['022.json', '005.json']:
    io.open(os.path.join(B, 'AI語譯', '_work', 'align_fix', '_loc_' + b.replace('.json', '.txt')), 'w',
            encoding='utf-8').write(run(b))
print('ok')
