# -*- coding: utf-8 -*-
"""重排後獨立複驗：直接讀最終 docx，重建戒單元，檢查結構。"""
import io, sys, hashlib, collections, importlib.util
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
spec = importlib.util.spec_from_file_location("fx", B + r"\_src\fix_hebian_jz2.py")
fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)

yp = fx.yuan_pairs(); yp, A = fx.assign(yp)
key = {}
for r in yp:
    key.setdefault((r['kind'], r['sub'] + r['body']), []).append(r)

ps = [p.text for p in Document(B + r"\白話\行事鈔資持記句級合編_卷中之二.docx").paragraphs if p.text.strip()]
body = ps[3:]
pairs = [(body[2*k], body[2*k+1]) for k in range(len(body)//2)]
print('組數', len(pairs))

seq = []
for tag, tr in pairs:
    kind, rest = fx.norm(tag)
    cand = key.get((kind, rest))
    assert cand, tag[:40]
    r = cand.pop(0)
    seq.append(r)
print('一對一還原', len(seq), '唯一', len({id(r) for r in seq}))

# 每戒：鈔是否全在記前、是否連續
ok = True
for u in range(1, len(fx.UNIT)+1):
    pos = [i for i, r in enumerate(seq) if r['u'] == u]
    kinds = [seq[i]['kind'] for i in pos]
    if not pos:
        print('空的單元', u); ok = False; continue
    if pos != list(range(pos[0], pos[0]+len(pos))):
        print('不連續', fx.UNIT[u-1][0]); ok = False
    if '記' in kinds and '鈔' in kinds:
        last_chao = max(i for i in range(len(kinds)) if kinds[i]=='鈔')
        first_ji = min(i for i in range(len(kinds)) if kinds[i]=='記')
        if last_chao > first_ji:
            print('記在鈔前', fx.UNIT[u-1][0]); ok = False
    if kinds[0] != '鈔':
        print('非鈔起頭', fx.UNIT[u-1][0]); ok = False
print('結構全部通過:', ok)
# 鈔/記 各自原序
cs = [r['num'] for r in seq if r['kind']=='鈔']
js = [r['num'] for r in seq if r['kind']=='記']
print('鈔序保持', cs == [r['num'] for r in fx.yuan_pairs() if r['kind']=='鈔'])
print('記序保持', js == [r['num'] for r in fx.yuan_pairs() if r['kind']=='記'])
# 指名的例子
i385 = [i for i,r in enumerate(seq) if r['num']==385 and r['kind']=='記'][0]
i68 = [i for i,r in enumerate(seq) if r['num']==68 and r['kind']=='鈔'][0]
print('記385 在 鈔68 之前:', i385 < i68, i385+1, i68+1)
# 內容雜湊
h = collections.Counter(hashlib.sha1((r['kind']+r['body']).encode()).hexdigest() for r in seq)
h0 = collections.Counter(hashlib.sha1((r['kind']+r['body']).encode()).hexdigest() for r in fx.yuan_pairs())
print('內容集合相同:', h == h0)
