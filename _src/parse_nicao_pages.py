# -*- coding: utf-8 -*-
"""尼鈔：解析 docs/nicao 頁面 pair，統計並輸出對照清單。"""
import io, os, re, html, json
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))
out = []
for vol in ('卷上', '卷中', '卷下'):
    t = io.open(os.path.join(B, 'docs', 'nicao', vol + '.html'), encoding='utf-8').read()
    sec = ''
    for m in re.finditer(r'<h2 class="sec"[^>]*>([^<]*)</h2>|<div class="pair[^"]*"><div class="o[^"]*">(.*?)</div><div class="t">(.*?)</div></div>', t, re.S):
        if m.group(1) is not None:
            sec = m.group(1)
            continue
        o = html.unescape(re.sub('<[^>]+>', '', m.group(2)))
        tr = html.unescape(re.sub('<[^>]+>', '', m.group(3)))
        lab = re.match(r'^【([^】]+)】', o)
        out.append({'vol': vol, 'sec': sec, 'label': lab.group(1) if lab else '', 'o': o, 't': tr})
print('pairs', len(out))
import collections
print('by vol', collections.Counter(x['vol'] for x in out))
print('by sec', collections.Counter(x['sec'] for x in out))
print('labels', collections.Counter(x['label'] for x in out))
for x in out[:5]:
    print(repr(x['o'][:60]), '|', repr(x['t'][:60]))
io.open(os.path.join(B, '_src', '_nicao_pages.json'), 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False))
