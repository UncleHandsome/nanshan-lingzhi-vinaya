# -*- coding: utf-8 -*-
"""For each entry, dump 原文/舊譯文 from 校閱_單段 snapshot + current 譯文."""
import io, os, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'entries.json'), encoding='utf-8'))
ents = d['uniq']

def snapshot(section):
    p = os.path.join(B, '校閱_單段', section + '.txt')
    if not os.path.exists(p):
        return None
    t = io.open(p, encoding='utf-8-sig').read()
    orig = re.search(r'【原文】(.*?)(?:\n【|$)', t, re.S)
    trans = re.search(r'【譯文】(.*)', t, re.S)
    return (orig.group(1).strip() if orig else ''), (trans.group(1).strip() if trans else '')

out = []
for k, e in enumerate(ents, 1):
    snap = snapshot(e['section'])
    out.append('=' * 100)
    out.append('[%02d] %s | %s | %s' % (k, e['gid'], e['level'], e['cat']))
    out.append('原文起首(報告)：' + e['orig'])
    out.append('問題：' + e['problem'])
    out.append('建議：' + e['suggestion'])
    out.append('-- 校閱_單段原檔 --')
    if snap:
        out.append('【原文】' + snap[0])
        out.append('【舊譯文】' + snap[1])
    else:
        out.append('(snapshot missing: %s)' % e['section'])
    out.append('')
io.open(os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'snap.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(ents))
