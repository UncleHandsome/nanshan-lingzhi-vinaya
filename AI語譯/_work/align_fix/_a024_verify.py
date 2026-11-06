#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify: compare assigned c with best n-gram overlap c for each 記段."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
hb = json.load(open(os.path.join(HERE, '_a024_hb.json'), encoding='utf-8'))
J = [t.replace('【記】', '').strip() for k, t in hb if k == 'J']
C = [t.replace('【鈔】', '').strip() for k, t in hb if k == 'C']
C = C[1:]  # drop 篇題 block so index == cand c
mp = {}
for x in json.load(open(os.path.join(HERE, 'out_024.json'), encoding='utf-8'))['map']:
    mp[x['z']] = x['c']

def grams(s, n=3):
    s = re.sub(r'[，。；：、！？「」〔〕（）《》\s]', '', s)
    return set(s[i:i+n] for i in range(len(s)-n+1))

Cc = [grams(c) for c in C]
report = []
bad = 0
for z, j in enumerate(J):
    g = grams(j)
    scores = [len(g & x) / (len(g) + 1) for x in Cc]
    best = max(range(len(scores)), key=lambda i: scores[i])
    a = mp[z]
    flag = ''
    if best != a:
        flag = '*'
        bad += 1
    report.append(f'z{z:2d} c{a:2d} best{best:2d} s[{a}]={scores[a]:.3f} s[best]={scores[best]:.3f} {flag} | {j[:34]}')
report.append(f'-- mismatches: {bad}/{len(J)}')
open(os.path.join(HERE, '_a024_verify.txt'), 'w', encoding='utf-8').write('\n'.join(report))
print('mismatch', bad, 'of', len(J))
