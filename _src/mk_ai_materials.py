# -*- coding: utf-8 -*-
"""整理五書待 AI 處理材料。"""
import io
import json
import os
import re
import html
from collections import Counter

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')
OUT = os.path.join(B, 'AI處理材料')
os.makedirs(OUT, exist_ok=True)
BOOKS = {
    'xingshichao': '行事鈔',
    'jieshu': '戒疏',
    'yeshu': '業疏',
    'nicao': '尼鈔',
    'yichao': '義鈔',
}


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


# 1. 未定位
for book, name in BOOKS.items():
    rows = [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'), encoding='utf-8') if x.strip()]
    miss = [r for r in rows if r.get('raw_start', -1) < 0]
    if not miss:
        continue
    out = ['# %s 未定位材料' % name, '', '- 數量：%d' % len(miss), '', '請判斷：卷別、是否重複、是否缺譯。', '']
    for r in miss:
        out.append('\n## %s\n\n【原文】\n\n%s\n\n【白話】\n\n%s\n' % (r['key'], r.get('source', '')[:800], r.get('translation', '')[:500]))
    io.open(os.path.join(OUT, '未定位_%s.md' % name), 'w', encoding='utf-8').write('\n'.join(out))
    print(name, '未定位', len(miss))

# 2. 戒蔬 render 差異
canon = {}
for line in io.open(os.path.join(C, 'jieshu.jsonl'), encoding='utf-8'):
    r = json.loads(line)
    for s in r.get('segments') or []:
        canon.setdefault(r.get('vol', ''), []).append((s.get('label', ''), s.get('source', ''), s.get('translation', '')))
page = {}
for v in ('卷一', '卷二', '卷三', '卷四'):
    t = io.open(os.path.join(B, 'docs', 'jieshu', v + '.html'), encoding='utf-8').read()
    for m in re.finditer(r'<div class="pair[^"]*"><div class="o[^"]*">(.*?)</div><div class="t">(.*?)</div></div>', t, re.S):
        o = html.unescape(re.sub('<[^>]+>', '', m.group(1)))
        tr = html.unescape(re.sub('<[^>]+>', '', m.group(2)))
        page.setdefault(v, []).append((han(o), tr, o))
out = ['# 戒蔬 render 與現頁差異', '', '請判斷：哪邊是正確的、是否重複、是否漏補。', '']
for v in ('卷二', '卷三', '卷四', '卷一'):
    cc = Counter([han(s) for _, s, _ in canon.get(v, [])])
    pc = Counter([s for s, _, _ in page.get(v, [])])
    only_c = cc - pc
    only_p = pc - cc
    out.append('\n## %s\n\n- 只在定稿：%d\n- 只在現頁：%d\n' % (v, sum(only_c.values()), sum(only_p.values())))
    for s, n in only_c.items():
        out.append('\n### 只在定稿\n\n%s\n' % s[:1000])
    for s, n in only_p.items():
        out.append('\n### 只在現頁\n\n%s\n' % s[:1000])
io.open(os.path.join(OUT, '戒蔬_render差異.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('diff written')
