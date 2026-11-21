# -*- coding: utf-8 -*-
"""比對定稿分段與目前 jieshu 頁面，列出只在一邊的 pair。"""
import io
import json
import os
import re
import html
from collections import Counter

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿', 'jieshu.jsonl')
LAB = ('疏文', '記文', '鈔文', '律文', '註文', '序文')


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


canon = {}
for line in io.open(C, encoding='utf-8'):
    r = json.loads(line)
    for s in r.get('segments') or []:
        canon.setdefault(r['vol'], []).append((s.get('label', ''), s.get('source', ''), s.get('translation', '')))
page = {}
for v in ('卷一', '卷二', '卷三', '卷四'):
    t = io.open(os.path.join(B, 'docs', 'jieshu', v + '.html'), encoding='utf-8').read()
    for m in re.finditer(r'<div class="pair[^"]*"><div class="o[^"]*">(.*?)</div><div class="t">(.*?)</div></div>', t, re.S):
        o = html.unescape(re.sub('<[^>]+>', '', m.group(1)))
        tr = html.unescape(re.sub('<[^>]+>', '', m.group(2)))
        page.setdefault(v, []).append((han(o), tr))
out = ['# 戒疏定稿 render 與現頁差異', '']
for v in ('卷一', '卷二', '卷三', '卷四'):
    cc = Counter([han(s) for _, s, _ in canon.get(v, [])])
    pc = Counter([s for s, _ in page.get(v, [])])
    only_c = cc - pc
    only_p = pc - cc
    out.append('## %s' % v)
    out.append('')
    out.append('- 定稿：%d' % sum(cc.values()))
    out.append('- 現頁：%d' % sum(pc.values()))
    out.append('- 只在定稿：%d' % sum(only_c.values()))
    out.append('- 只在現頁：%d' % sum(only_p.values()))
    out.append('')
    for s, n in list(only_c.items())[:10]:
        out.append('- 只在定稿：%s' % s[:80])
    for s, n in list(only_p.items())[:10]:
        out.append('- 只在現頁：%s' % s[:80])
    out.append('')
fp = os.path.join(B, '重作材料_長段', '戒蔬_render_diff.md')
io.open(fp, 'w', encoding='utf-8').write('\n'.join(out))
print(fp)
