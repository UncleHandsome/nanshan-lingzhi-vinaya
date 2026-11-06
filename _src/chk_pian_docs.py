# -*- coding: utf-8 -*-
"""檢查 9 篇會本：鈔記順序、空白鈔、白話比例"""
import io, os, re, glob
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
for f in sorted(glob.glob(os.path.join(B, '白話', '會本_篇0*.docx'))) + [os.path.join(B, '白話', '會本_篇10_說戒正儀.docx')]:
    d = Document(f)
    ps = [p.text.strip() for p in d.paragraphs]
    seq = []          # (type, num, tr_len)
    for i, t in enumerate(ps):
        m = re.match(r'^【鈔(\d+)】', t)
        if m:
            seq.append(('c', int(m.group(1)), 0))
            continue
        m = re.match(r'^【記(\d+)】', t)
        if m:
            tr = ps[i + 1] if i + 1 < len(ps) else ''
            seq.append(('j', int(m.group(1)), han(tr)))
    nc = sum(1 for x in seq if x[0] == 'c')
    nj = sum(1 for x in seq if x[0] == 'j')
    empty = [x[1] for x in seq if x[0] == 'j' and x[2] < 5]
    # 記序是否大致遞增
    nums = [x[1] for x in seq if x[0] == 'j']
    inv = sum(1 for a, b in zip(nums, nums[1:]) if b < a)
    # 沒有記的鈔
    cur = None
    has = {}
    for x in seq:
        if x[0] == 'c':
            cur = x[1]; has.setdefault(cur, False)
        elif cur:
            has[cur] = True
    noji = [k for k, v in has.items() if not v]
    print('%-22s 鈔%3d 記片%3d 空白譯%2d 逆序%2d 無記鈔%s' % (
        os.path.basename(f)[:-5], nc, nj, len(empty), inv, noji[:6]))
