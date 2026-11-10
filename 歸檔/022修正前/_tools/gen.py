# -*- coding: utf-8 -*-
"""依修正後的 out 與 TXT_分卷 重新產生 022 檔校閱材料，切成 5 份。"""
import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DST = os.path.join(B, '測試_022_修正版')
PROMPT = io.open(os.path.join(B, '校閱批次', '提示詞_白話校閱.md'), encoding='utf-8').read().rstrip('\n')

segs = json.load(io.open(os.path.join(B, '_tmp022', 'segs.json'), encoding='utf-8'))
assert [s['id'] for s in segs] == ['022-%04d' % i for i in range(1, 27)]


def src_paras(chunk):
    p = os.path.join(B, 'TXT_分卷', '01_行事鈔', chunk + '.txt')
    return [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n')[5:] if x.strip()]


def tr_paras(chunk):
    p = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', chunk + '.txt')
    return [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8', newline='').read()) if x.strip()]


S = {c: src_paras(c) for c in ('07b_卷中之三', '07c_卷中之三')}
T = {c: tr_paras(c) for c in ('07b_卷中之三', '07c_卷中之三')}

blocks = []
for s in segs:
    orig = S[s['chunk']][s['seg'] - 1]
    trans = T[s['chunk']][s['seg'] - 1]
    assert orig == s['orig'], s['id']
    blocks.append('【%s】01_行事鈔/%s#%d\n【原文】%s\n【譯文】%s' % (s['id'], s['chunk'], s['seg'], orig, trans))

prefix = '# 校閱材料\u3000第022檔\n\n以下提示詞請連同材料一起貼給 AI：\n\n'
head = prefix + PROMPT + '\n\n---\n\n# 材料開始\n\n'

os.makedirs(DST, exist_ok=True)
splits = [blocks[0:6], blocks[6:12], blocks[12:18], blocks[18:24], blocks[24:26]]
assert sum(len(x) for x in splits) == 26
for n, part in enumerate(splits, 1):
    txt = head + '\n\n'.join(part) + '\n'
    p = os.path.join(DST, '校閱_022_%d.txt' % n)
    io.open(p, 'w', encoding='utf-8', newline='\r\n').write(txt)
    print('%s  %d 段  %d bytes  ids %s..%s' % (os.path.basename(p), len(part),
          len(txt.encode('utf-8')), part[0][:11], part[-1][:11]))
